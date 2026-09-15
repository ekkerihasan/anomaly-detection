"""Applies db/schema.sql to DATABASE_URL. No migration framework per
CLAUDE.md rule 8 — this is a one-shot DDL apply, run by hand.

Usage: python scripts/apply_schema.py
Requires DATABASE_URL in .env or the environment.
"""
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "db" / "schema.sql"


def main():
    load_dotenv(ROOT / ".env")
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL not set. Copy .env.example to .env and fill it in.")

    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print(f"Applied {SCHEMA_PATH} to {database_url.split('@')[-1]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
