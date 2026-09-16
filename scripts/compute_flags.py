"""
Computes the six deterministic flags (MHASH26-BUILD-PLAN.md Section 8)
over the loaded slice and writes rows into `flag`, each with a severity
and an `evidence` JSONB blob the explanation UI renders from directly
(CLAUDE.md rule 3). All thresholds come from config/weights.yaml
(CLAUDE.md rule 4) -- none are hardcoded here.

This is a batch/offline computation, not part of the request path -- the
"all scoring is server-side" rule (5) is about the frontend never
computing scores, not about where in the pipeline this script sits.

Usage: python scripts/compute_flags.py
"""
import os
from pathlib import Path

import psycopg2
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


def load_weights():
    with open(ROOT / "config" / "weights.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["flags"]


def compute_f1_single_bid(cur, w):
    f1 = w["F1_SINGLE_BID"]
    cur.execute(
        """
        INSERT INTO flag (award_id, code, severity, evidence)
        SELECT a.id, 'F1_SINGLE_BID',
            CASE WHEN a.contract_value > %(high_value_threshold_inr)s
                 THEN %(severity_above)s ELSE %(severity_below)s END,
            jsonb_build_object(
                'bids_received', a.bids_received,
                'tender_type', t.tender_type,
                'peer_median_bids', ROUND(peer.median_bids::numeric, 1)
            )
        FROM award a
        JOIN tender t ON t.id = a.tender_id
        JOIN (
            SELECT t2.org_id,
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY a2.bids_received) AS median_bids
            FROM award a2 JOIN tender t2 ON t2.id = a2.tender_id
            WHERE t2.tender_type ILIKE %(open_pattern)s AND a2.bids_received IS NOT NULL
            GROUP BY t2.org_id
        ) peer ON peer.org_id = t.org_id
        WHERE a.bids_received = 1 AND t.tender_type ILIKE %(open_pattern)s
        """,
        {
            "high_value_threshold_inr": f1["high_value_threshold_inr"],
            "severity_above": f1["severity_above_threshold"],
            "severity_below": f1["severity_below_threshold"],
            "open_pattern": "%open%",
        },
    )
    return cur.rowcount


def compute_f2_short_window(cur, w):
    f2 = w["F2_SHORT_WINDOW"]
    cur.execute(
        """
        INSERT INTO flag (award_id, code, severity, evidence)
        SELECT a.id, 'F2_SHORT_WINDOW',
            GREATEST(%(sev_floor)s, LEAST(%(sev_ceil)s,
                CASE
                    WHEN (t.bid_end_date - t.epublished_date) <= %(ceil_days)s THEN %(sev_ceil)s
                    ELSE %(sev_ceil)s - ((t.bid_end_date - t.epublished_date) - %(ceil_days)s)::numeric
                         / (%(floor_days)s - %(ceil_days)s) * (%(sev_ceil)s - %(sev_floor)s)
                END
            )),
            jsonb_build_object(
                'window_days', (t.bid_end_date - t.epublished_date),
                'required_days', %(required_days)s,
                'epublished_date', t.epublished_date,
                'bid_end_date', t.bid_end_date
            )
        FROM award a
        JOIN tender t ON t.id = a.tender_id
        WHERE t.epublished_date IS NOT NULL AND t.bid_end_date IS NOT NULL
              AND (t.bid_end_date - t.epublished_date) < %(required_days)s
              AND (t.bid_end_date - t.epublished_date) >= 0
        """,
        {
            "required_days": f2["required_days"],
            "ceil_days": f2["severity_at_or_below_days"],
            "floor_days": f2["severity_floor_days"],
            "sev_ceil": f2["severity_ceiling"],
            "sev_floor": f2["severity_floor"],
        },
    )
    return cur.rowcount


def compute_f5_threshold_bunching(cur, w):
    f5 = w["F5_THRESHOLD_BUNCHING"]
    total = 0
    for entry in f5["thresholds_inr"]:
        cur.execute(
            """
            INSERT INTO flag (award_id, code, severity, evidence)
            SELECT a.id, 'F5_THRESHOLD_BUNCHING',
                CASE WHEN (%(threshold)s - a.contract_value)::numeric / %(threshold)s <= %(tight_pct)s
                     THEN %(sev_tight)s ELSE %(sev_wide)s END,
                jsonb_build_object(
                    'contract_value', a.contract_value,
                    'threshold', %(threshold)s,
                    'gap_pct', ROUND((%(threshold)s - a.contract_value)::numeric / %(threshold)s, 4),
                    'rule', %(rule)s
                )
            FROM award a
            WHERE a.contract_value <= %(threshold)s
                  AND a.contract_value > %(threshold)s * (1 - %(wide_pct)s)
            """,
            {
                "threshold": entry["amount"],
                "rule": entry["rule"],
                "tight_pct": f5["tight_band_pct"],
                "wide_pct": f5["wide_band_pct"],
                "sev_tight": f5["severity_tight"],
                "sev_wide": f5["severity_wide"],
            },
        )
        total += cur.rowcount
    return total


def compute_f9_instant_award(cur, w):
    f9 = w["F9_INSTANT_AWARD"]
    cur.execute(
        """
        INSERT INTO flag (award_id, code, severity, evidence)
        SELECT a.id, 'F9_INSTANT_AWARD',
            CASE WHEN (a.contract_date - t.bid_open_date) <= 0
                 THEN %(sev_0)s ELSE %(sev_1)s END,
            jsonb_build_object(
                'decision_days', (a.contract_date - t.bid_open_date),
                'bid_open_date', t.bid_open_date,
                'contract_date', a.contract_date,
                'peer_median_days', ROUND(peer.median_days::numeric, 1)
            )
        FROM award a
        JOIN tender t ON t.id = a.tender_id
        JOIN (
            SELECT t2.org_id,
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY (a2.contract_date - t2.bid_open_date)) AS median_days
            FROM award a2 JOIN tender t2 ON t2.id = a2.tender_id
            WHERE t2.bid_open_date IS NOT NULL AND a2.contract_date IS NOT NULL
            GROUP BY t2.org_id
        ) peer ON peer.org_id = t.org_id
        WHERE t.bid_open_date IS NOT NULL AND a.contract_date IS NOT NULL
              AND (a.contract_date - t.bid_open_date) <= 1
        """,
        {
            "sev_0": f9["severity_at_0_days"],
            "sev_1": f9["severity_at_1_day"],
        },
    )
    return cur.rowcount


def compute_f11_emd_anomaly(cur, w):
    f11 = w["F11_EMD_ANOMALY"]
    cur.execute(
        """
        WITH ratios AS (
            SELECT a.id AS award_id, t.org_id, t.emd, a.contract_value,
                   t.emd / a.contract_value AS ratio
            FROM award a JOIN tender t ON t.id = a.tender_id
            WHERE t.emd IS NOT NULL AND a.contract_value IS NOT NULL AND a.contract_value > 0
        ),
        -- Postgres does not allow OVER on an ordered-set aggregate, so the
        -- per-organisation median is computed as its own grouped CTE and
        -- joined back, rather than as a window function over `ratios`.
        medians AS (
            SELECT org_id,
                   PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ratio) AS median_ratio
            FROM ratios
            GROUP BY org_id
        ),
        ranked AS (
            SELECT r.*, m.median_ratio,
                   PERCENT_RANK() OVER (PARTITION BY r.org_id ORDER BY r.ratio) AS pr
            FROM ratios r
            JOIN medians m ON m.org_id = r.org_id
        )
        INSERT INTO flag (award_id, code, severity, evidence)
        SELECT award_id, 'F11_EMD_ANOMALY',
            CASE
                WHEN pr <= %(pct_bottom)s THEN %(sev_min)s + (%(sev_max)s - %(sev_min)s) * ((%(pct_bottom)s - pr) / %(pct_bottom)s)
                ELSE %(sev_min)s + (%(sev_max)s - %(sev_min)s) * ((pr - %(pct_top)s) / (1 - %(pct_top)s))
            END,
            jsonb_build_object(
                'emd', emd,
                'contract_value', contract_value,
                'ratio', ROUND(ratio::numeric, 4),
                'peer_ratio_median', ROUND(median_ratio::numeric, 4)
            )
        FROM ranked
        WHERE pr <= %(pct_bottom)s OR pr >= %(pct_top)s
        """,
        {
            "pct_bottom": f11["percentile_bottom"],
            "pct_top": f11["percentile_top"],
            "sev_min": f11["severity_min"],
            "sev_max": f11["severity_max"],
        },
    )
    return cur.rowcount


def compute_f12_year_end_rush(cur, w):
    f12 = w["F12_YEAR_END_RUSH"]
    days_in_month = 31 if f12["month"] in (1, 3, 5, 7, 8, 10, 12) else 30
    window_days = days_in_month - f12["day_from"] + 1
    annual_share_baseline = window_days / 365.0

    cur.execute(
        """
        WITH org_totals AS (
            SELECT t.org_id, COUNT(*) AS total_awards,
                COUNT(*) FILTER (
                    WHERE EXTRACT(MONTH FROM a.contract_date) = %(month)s
                          AND EXTRACT(DAY FROM a.contract_date) >= %(day_from)s
                ) AS rush_awards
            FROM award a JOIN tender t ON t.id = a.tender_id
            WHERE a.contract_date IS NOT NULL
            GROUP BY t.org_id
        )
        INSERT INTO flag (award_id, code, severity, evidence)
        SELECT a.id, 'F12_YEAR_END_RUSH', %(severity)s,
            jsonb_build_object(
                'contract_date', a.contract_date,
                'org_march_share', ROUND(ot.rush_awards::numeric / ot.total_awards, 4),
                'org_annual_share', ROUND(%(annual_share)s::numeric, 4)
            )
        FROM award a
        JOIN tender t ON t.id = a.tender_id
        JOIN org_totals ot ON ot.org_id = t.org_id
        WHERE EXTRACT(MONTH FROM a.contract_date) = %(month)s
              AND EXTRACT(DAY FROM a.contract_date) >= %(day_from)s
        """,
        {
            "month": f12["month"],
            "day_from": f12["day_from"],
            "severity": f12["severity"],
            "annual_share": annual_share_baseline,
        },
    )
    return cur.rowcount


def main():
    load_dotenv(ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL not set.")

    weights = load_weights()

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    print("Clearing existing flags...")
    cur.execute("TRUNCATE flag RESTART IDENTITY")
    conn.commit()

    steps = [
        ("F1_SINGLE_BID", compute_f1_single_bid),
        ("F2_SHORT_WINDOW", compute_f2_short_window),
        ("F5_THRESHOLD_BUNCHING", compute_f5_threshold_bunching),
        ("F9_INSTANT_AWARD", compute_f9_instant_award),
        ("F11_EMD_ANOMALY", compute_f11_emd_anomaly),
        ("F12_YEAR_END_RUSH", compute_f12_year_end_rush),
    ]

    for name, fn in steps:
        print(f"Computing {name}...")
        count = fn(cur, weights)
        conn.commit()
        print(f"  {count:,} flags written")

    cur.execute("SELECT COUNT(*), COUNT(DISTINCT award_id) FROM flag")
    total, distinct_awards = cur.fetchone()
    print(f"\nTotal: {total:,} flag rows across {distinct_awards:,} distinct awards")

    conn.close()


if __name__ == "__main__":
    main()
