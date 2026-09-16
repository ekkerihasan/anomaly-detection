"""
Composite risk score and ranking (MHASH26-BUILD-PLAN.md Section 8).

    score = SUM( weight[code] * severity ) over every flag on that award

Weights come from config/weights.yaml and nowhere else (CLAUDE.md rule 4).
Ranking is dense-rank over the loaded slice only -- this is deliberately
NOT a national percentile, because we have not computed one and the plan
(Section 8) forbids claiming it.

Awards carrying no flags get no risk_score row at all rather than a zero.
A zero would be indistinguishable from "scored and found clean", and the
ranked list is a review queue, not a scoreboard of every award.

Run after scripts/compute_flags.py.
Usage: python scripts/compute_scores.py
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


def main():
    load_dotenv(ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL not set. Copy .env.example to .env and fill it in.")

    weights = load_weights()

    # Passed to SQL as a (code, weight) list so the arithmetic happens in one
    # pass server-side, while the numbers still originate in the YAML.
    weight_pairs = [(code, float(cfg["weight"])) for code, cfg in weights.items()]

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM flag")
            n_flags = cur.fetchone()[0]
            if n_flags == 0:
                raise SystemExit(
                    "No rows in `flag`. Run scripts/compute_flags.py first."
                )

            # Any flag code present in the data but absent from weights.yaml
            # would be silently dropped from the score. Fail loudly instead.
            cur.execute("SELECT DISTINCT code FROM flag")
            seen = {r[0] for r in cur.fetchall()}
            configured = {c for c, _ in weight_pairs}
            unknown = seen - configured
            if unknown:
                raise SystemExit(
                    f"Flag code(s) {sorted(unknown)} present in `flag` but missing "
                    f"from config/weights.yaml -- refusing to score with an "
                    f"incomplete weight set."
                )

            print("Clearing existing scores...")
            cur.execute("TRUNCATE risk_score")

            print("Computing composite scores and ranks...")
            cur.execute(
                """
                WITH w(code, weight) AS (
                    SELECT * FROM unnest(%(codes)s::text[], %(weights)s::numeric[])
                ),
                scored AS (
                    SELECT f.award_id,
                           SUM(w.weight * f.severity) AS score
                    FROM flag f
                    JOIN w ON w.code = f.code
                    GROUP BY f.award_id
                )
                INSERT INTO risk_score (award_id, score, rank)
                SELECT award_id,
                       ROUND(score, 4),
                       DENSE_RANK() OVER (ORDER BY score DESC)
                FROM scored
                """,
                {
                    "codes": [c for c, _ in weight_pairs],
                    "weights": [w for _, w in weight_pairs],
                },
            )
            written = cur.rowcount

        conn.commit()

        with conn.cursor() as cur:
            cur.execute(
                "SELECT round(min(score),3), round(max(score),3), "
                "round(avg(score),3), max(rank) FROM risk_score"
            )
            lo, hi, avg, max_rank = cur.fetchone()
            cur.execute(
                """
                SELECT r.rank, r.score, o.name,
                       string_agg(f.code, ',' ORDER BY f.code)
                FROM risk_score r
                JOIN award a   ON a.id = r.award_id
                JOIN tender t  ON t.id = a.tender_id
                JOIN organisation o ON o.id = t.org_id
                JOIN flag f    ON f.award_id = r.award_id
                GROUP BY r.rank, r.score, o.name
                ORDER BY r.score DESC
                LIMIT 5
                """
            )
            top = cur.fetchall()

        print(f"\nScored {written:,} awards (min {lo}, max {hi}, avg {avg}, "
              f"{max_rank:,} distinct ranks).")
        print("\nTop 5 by score:")
        for rank, score, org, codes in top:
            print(f"  #{rank:<4} {score:>6}  {org:<36} {codes}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
