"""
SYNTHETIC INJECTION BACK-TEST (MHASH26-BUILD-PLAN.md Section 9, fallback path).

The plan's preferred back-test is against the Assam Police Housing Corporation
bid-rigging case (CCI order, 7 April 2026). Those tenders are NOT in this
corpus -- docs/h4-data-report.md records the search that established this.
Section 9 is explicit about what to do then:

    "do not fake it. Fall back to a synthetic injection test. Take a clean
     organisation's real award history, programmatically inject a splitting
     pattern and a rotation pattern, report precision-at-K, and say
     explicitly on screen that it is synthetic."

So that is what this does. It plants a known set of award rows carrying the
shape of a real procurement fraud, re-runs the *unmodified* detection engine
over the whole slice, and measures where the planted awards rank. The engine
is never told which rows are planted.

What "precision at K" means here, and why not accuracy: there is no labelled
negative set and there never will be -- an award that was never investigated
is not thereby clean. So the honest question is "if an auditor reads the top
K, how many of the known-bad ones do they find?", not "what fraction of all
awards did we classify correctly".

Every planted row is marked in `award.detail_url` with INJECTION_MARKER so it
can be identified and removed. Nothing is written to the real award tables
without that marker.

Usage:
    python scripts/backtest_synthetic.py            # inject, score, report
    python scripts/backtest_synthetic.py --cleanup  # remove planted rows only
"""
import argparse
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

# Every planted award carries this in its detail_url. It is the only way the
# rows are distinguishable from real ones, so it must never be removed.
INJECTION_MARKER = "SYNTHETIC-BACKTEST-INJECTION"

REPORT_PATH = ROOT / "docs" / "backtest-report.md"


def db_connect():
    load_dotenv(ROOT / ".env")
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL not set. Copy .env.example to .env and fill it in.")
    return psycopg2.connect(url)


def cleanup(conn, quiet=False):
    """Removes every planted row and its derived flags/scores/reviews."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM award WHERE detail_url LIKE %s", (f"%{INJECTION_MARKER}%",)
        )
        award_ids = [r[0] for r in cur.fetchall()]
        if not award_ids:
            if not quiet:
                print("No planted rows to remove.")
            return 0

        cur.execute("DELETE FROM flag WHERE award_id = ANY(%s)", (award_ids,))
        cur.execute("DELETE FROM risk_score WHERE award_id = ANY(%s)", (award_ids,))
        cur.execute("DELETE FROM review WHERE award_id = ANY(%s)", (award_ids,))
        cur.execute("DELETE FROM award WHERE id = ANY(%s)", (award_ids,))
        cur.execute(
            "DELETE FROM tender WHERE detail_url LIKE %s", (f"%{INJECTION_MARKER}%",)
        )
        cur.execute(
            "DELETE FROM vendor WHERE name_raw LIKE %s", ("[BACKTEST]%",)
        )
    conn.commit()
    if not quiet:
        print(f"Removed {len(award_ids)} planted awards and their derived rows.")
    return len(award_ids)


def pick_host_organisation(cur):
    """Picks the organisation with the most awards to host the injection.

    A big host is deliberate: the planted rows have to compete against a
    large, realistic population, otherwise ranking them highly proves nothing.
    """
    cur.execute(
        """
        SELECT o.id, o.name, count(a.id) AS n
        FROM organisation o
        JOIN tender t ON t.org_id = o.id
        JOIN award a  ON a.tender_id = t.id
        GROUP BY o.id, o.name
        ORDER BY n DESC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    if row is None:
        raise SystemExit("No organisations with awards found. Load a slice first.")
    return row


def inject(conn):
    """Plants two documented fraud patterns into a real organisation's history.

    Pattern A -- demand splitting. One requirement that should have gone out
    as a single ~Rs 2 crore tender, broken into five awards each landing just
    under the Rs 50 lakh limited-tender-enquiry threshold (GFR Rule 162),
    same month, same buyer. This is a standing CAG finding and the reason
    F5_THRESHOLD_BUNCHING exists.

    Pattern B -- bid rotation with cover bidding. Four vendors take turns
    winning eight tenders in a fixed cycle, each won on a single bid after a
    compressed submission window. This is the shape of the Assam case: the
    engine does not detect "rotation" as such (that detector is explicitly out
    of scope, CLAUDE.md rule 1) -- it detects the single bids, short windows
    and instant awards the rotation is executed through.
    """
    planted = []

    with conn.cursor() as cur:
        org_id, org_name, org_awards = pick_host_organisation(cur)
        print(f"Host organisation: {org_name} ({org_awards:,} real awards)")

        # Vendors used by the planted awards. Fictional, and marked.
        vendor_ids = []
        for name in [
            "[BACKTEST] Alpha Works Pvt Ltd",
            "[BACKTEST] Beta Constructions",
            "[BACKTEST] Gamma Infra Pvt Ltd",
            "[BACKTEST] Delta Engineering Co",
        ]:
            cur.execute(
                "INSERT INTO vendor (name_raw, name_norm) VALUES (%s, %s) RETURNING id",
                (name, " ".join(name.lower().split())),
            )
            vendor_ids.append(cur.fetchone()[0])

        def plant(title, value, epub, bid_end, bid_open, contract_date,
                  bids, emd, vendor_id, pattern):
            cur.execute(
                """
                INSERT INTO tender (ref_no, org_id, title, description, category,
                    product_category, tender_type, epublished_date, bid_start_date,
                    bid_end_date, bid_open_date, emd, tender_fee, detail_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
                """,
                (f"BACKTEST/{pattern}/{len(planted)+1}", org_id, title,
                 f"Synthetic back-test row, pattern {pattern}.", "Works",
                 "Civil Works", "Open Tender", epub, epub, bid_end, bid_open,
                 emd, 1000, f"https://example.invalid/{INJECTION_MARKER}"),
            )
            tender_id = cur.fetchone()[0]
            cur.execute(
                """
                INSERT INTO award (tender_id, vendor_id, contract_value,
                    contract_date, bids_received, completion_days, detail_url)
                VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id
                """,
                (tender_id, vendor_id, value, contract_date, bids, 180,
                 f"https://example.invalid/{INJECTION_MARKER}"),
            )
            award_id = cur.fetchone()[0]
            planted.append((award_id, pattern))

        # ---- Pattern A: demand splitting under the Rs 50 lakh threshold ----
        base = date(2023, 3, 6)
        for i in range(5):
            value = 4_940_000 + i * 12_000          # Rs 49.4L - 49.9L
            epub = base + timedelta(days=i * 2)
            bid_end = epub + timedelta(days=12)     # short window, GFR wants 21
            bid_open = bid_end
            contract = bid_open + timedelta(days=1)
            plant(
                title=f"Site development works - package {i+1} of 5",
                value=value, epub=epub, bid_end=bid_end, bid_open=bid_open,
                contract_date=contract, bids=1,
                emd=round(value * 0.02, 2),
                vendor_id=vendor_ids[0],
                pattern="A_SPLITTING",
            )

        # ---- Pattern B: rotation, four vendors cycling over eight tenders ---
        base = date(2023, 6, 12)
        for i in range(8):
            value = 7_200_000 + (i % 3) * 450_000
            epub = base + timedelta(days=i * 21)
            bid_end = epub + timedelta(days=9)      # compressed window
            bid_open = bid_end
            contract = bid_open                     # same-day award
            plant(
                title=f"Electrification of site block {chr(65+i)}",
                value=value, epub=epub, bid_end=bid_end, bid_open=bid_open,
                contract_date=contract, bids=1,
                emd=0,                              # no deterrent to a cover bid
                vendor_id=vendor_ids[i % 4],        # the rotation itself
                pattern="B_ROTATION",
            )

    conn.commit()
    print(f"Planted {len(planted)} awards "
          f"({sum(1 for _, p in planted if p == 'A_SPLITTING')} splitting, "
          f"{sum(1 for _, p in planted if p == 'B_ROTATION')} rotation).")
    return planted, org_name


def run(script):
    """Runs a pipeline script with the same interpreter, failing loudly."""
    print(f"\n--- running {script} ---")
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / script)],
                         capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        raise SystemExit(f"{script} failed.")
    print(res.stdout.strip().splitlines()[-1] if res.stdout.strip() else "(no output)")


def measure(conn, planted):
    """Reports where the planted awards landed in the ranking."""
    planted_ids = [a for a, _ in planted]

    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM risk_score")
        total_scored = cur.fetchone()[0]

        cur.execute(
            """
            SELECT award_id, score, rank
            FROM risk_score
            WHERE award_id = ANY(%s)
            ORDER BY score DESC
            """,
            (planted_ids,),
        )
        rows = cur.fetchall()

        # Position within the full ordering, not the dense rank -- "how many
        # rows would an auditor read before reaching this one".
        cur.execute(
            """
            WITH ordered AS (
                SELECT award_id, ROW_NUMBER() OVER (ORDER BY score DESC, award_id) AS pos
                FROM risk_score
            )
            SELECT award_id, pos FROM ordered WHERE award_id = ANY(%s)
            """,
            (planted_ids,),
        )
        positions = dict(cur.fetchall())

    detected = len(rows)
    by_pattern = {}
    for award_id, pattern in planted:
        by_pattern.setdefault(pattern, []).append(positions.get(award_id))

    results = {
        "total_scored": total_scored,
        "planted": len(planted),
        "detected": detected,
        "positions": positions,
        "by_pattern": by_pattern,
    }

    print("\n" + "=" * 62)
    print("SYNTHETIC INJECTION BACK-TEST RESULT")
    print("=" * 62)
    print(f"Slice size (awards carrying >=1 flag): {total_scored:,}")
    print(f"Planted fraudulent awards:             {len(planted)}")
    print(f"Flagged by the engine:                 {detected} "
          f"({detected / len(planted) * 100:.0f}% recall)")

    if positions:
        ordered_positions = sorted(p for p in positions.values() if p)
        worst = ordered_positions[-1]
        print(f"Worst-ranked planted award:            #{worst:,} of {total_scored:,}"
              f"  (top {worst / total_scored * 100:.2f}%)")

        print("\nPrecision / recall at review budget K:")
        print(f"  {'K':>8}  {'planted found':>14}  {'recall':>8}  {'precision':>10}")
        for k in (10, 25, 50, 100, 250, 500):
            if k > total_scored:
                continue
            found = sum(1 for p in ordered_positions if p <= k)
            print(f"  {k:>8}  {found:>14}  {found / len(planted) * 100:>7.0f}%  "
                  f"{found / k * 100:>9.1f}%")

        print("\nBy injected pattern:")
        for pattern, pos in sorted(by_pattern.items()):
            found = [p for p in pos if p]
            if found:
                print(f"  {pattern:<14} {len(found)}/{len(pos)} flagged, "
                      f"best #{min(found):,}, worst #{max(found):,}")
            else:
                print(f"  {pattern:<14} 0/{len(pos)} flagged")

    print("=" * 62)
    return results


def write_report(results, org_name, planted):
    total = results["total_scored"]
    positions = [p for p in results["positions"].values() if p]
    ordered = sorted(positions)

    lines = [
        "# Synthetic injection back-test",
        "",
        "> **This is a synthetic benchmark.** The awards measured here were",
        "> generated by `scripts/backtest_synthetic.py` and planted into the",
        "> loaded slice. They are not real procurement records and no real",
        "> organisation or vendor is accused of anything.",
        "",
        "## Why synthetic",
        "",
        "MHASH26-BUILD-PLAN.md Section 9 asks for a back-test against the Assam",
        "Police Housing Corporation bid-rigging case (CCI order, 7 April 2026).",
        "Those tenders are not present in this corpus — see",
        "`docs/h4-data-report.md` for the search that established that. Section 9",
        "names the fallback explicitly: inject a splitting pattern and a rotation",
        "pattern into a clean organisation's real history, report precision-at-K,",
        "and disclose that it is synthetic. That is what this is.",
        "",
        "## Method",
        "",
        f"- Host organisation: **{org_name}** (the largest in the slice, so the",
        "  planted rows compete against a realistic population).",
        f"- Planted awards: **{len(planted)}** — "
        f"{sum(1 for _, p in planted if p == 'A_SPLITTING')} demand-splitting, "
        f"{sum(1 for _, p in planted if p == 'B_ROTATION')} bid-rotation.",
        "- The detection engine was **not modified and not told which rows were",
        "  planted**. `compute_flags.py` and `compute_scores.py` ran unchanged.",
        "- Metric is precision/recall at a review budget K, not accuracy: there",
        "  is no labelled negative set, and an award nobody investigated is not",
        "  thereby clean.",
        "",
        "## Result",
        "",
        f"- Awards carrying at least one flag in the slice: **{total:,}**",
        f"- Planted awards detected: **{results['detected']}/{results['planted']}**",
    ]

    if ordered:
        lines += [
            f"- Worst-ranked planted award: **#{ordered[-1]:,} of {total:,}** "
            f"(top {ordered[-1] / total * 100:.2f}%)",
            "",
            "| Review budget K | Planted found | Recall | Precision |",
            "|---:|---:|---:|---:|",
        ]
        for k in (10, 25, 50, 100, 250, 500):
            if k > total:
                continue
            found = sum(1 for p in ordered if p <= k)
            lines.append(
                f"| {k} | {found} | {found / len(planted) * 100:.0f}% | "
                f"{found / k * 100:.1f}% |"
            )

    lines += [
        "",
        "## How to reproduce",
        "",
        "```",
        "python scripts/backtest_synthetic.py",
        "python scripts/backtest_synthetic.py --cleanup   # remove planted rows",
        "```",
        "",
        "Re-run against the real slice once it is loaded; the numbers above are",
        "whatever was in the database at the time this file was written.",
    ]

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {REPORT_PATH.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cleanup", action="store_true",
                    help="remove planted rows and exit")
    args = ap.parse_args()

    conn = db_connect()
    try:
        if args.cleanup:
            cleanup(conn)
            print("Re-run compute_flags.py and compute_scores.py to restore "
                  "the ranking without the planted rows.")
            return

        # Always start from a clean state so repeated runs don't stack.
        cleanup(conn, quiet=True)
        planted, org_name = inject(conn)
    finally:
        conn.close()

    run("compute_flags.py")
    run("compute_scores.py")

    conn = db_connect()
    try:
        results = measure(conn, planted)
    finally:
        conn.close()

    write_report(results, org_name, planted)


if __name__ == "__main__":
    main()
