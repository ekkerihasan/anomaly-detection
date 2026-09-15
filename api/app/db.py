"""Thin psycopg2 connection helper. No ORM per CLAUDE.md rule 8 — the six
flags and the scoring query are hand-written SQL, and staying close to the
driver keeps that honest."""
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from app.config import get_settings


@contextmanager
def get_conn():
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env and fill it in."
        )
    conn = psycopg2.connect(settings.database_url)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
            conn.commit()
