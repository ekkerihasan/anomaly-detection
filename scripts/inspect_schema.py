"""Inspects a downloaded CPPP mirror SQLite file: table names, columns,
row counts, and a couple of sample rows per table. Run this before writing
any ETL/profiling code that assumes specific column names — the plan text
gives field *names* (e.g. "Number of bids received"), not the actual
SQLite column identifiers, and those are never assumed here.

Usage: python scripts/inspect_schema.py data/raw/aoc_tenders.db
"""
import sqlite3
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print(f"usage: python {sys.argv[0]} <path-to-sqlite-db>")
        sys.exit(1)

    db_path = Path(sys.argv[1])
    if not db_path.exists():
        print(f"not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    tables = [
        r["name"]
        for r in cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    ]
    print(f"Tables in {db_path.name}: {tables}\n")

    for table in tables:
        print(f"=== {table} ===")
        cols = cur.execute(f"PRAGMA table_info({table})").fetchall()
        for c in cols:
            print(f"  {c['name']:<30} {c['type']}")

        count = cur.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
        print(f"  row count: {count:,}")

        print("  sample row:")
        sample = cur.execute(f"SELECT * FROM {table} LIMIT 1").fetchone()
        if sample:
            for key in sample.keys():
                val = str(sample[key])
                if len(val) > 120:
                    val = val[:120] + "..."
                print(f"    {key}: {val}")
        print()

    conn.close()


if __name__ == "__main__":
    main()
