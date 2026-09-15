# Automated Public Procurement Anomaly Detection

M#26 hackathon Round 1 build. Ranks government tender awards by how much
they deviate from normal procurement behaviour and shows an auditor why,
so scarce human review time lands on the tenders most worth reading.

Full plan, rationale, and rules for this repo live in
[`MHASH26-BUILD-PLAN.md`](./MHASH26-BUILD-PLAN.md) and
[`CLAUDE.md`](./CLAUDE.md) — read both before changing scope or
architecture.

## Data source

Public CPPP mirror (`https://tender.sarthaksidhant.com/`), citing
`eprocure.gov.in` as the origin. SHA-256 is verified before use — see
`scripts/download_verify.py`.

## Layout

```
config/weights.yaml   flag weights & thresholds (never hardcoded elsewhere)
db/schema.sql          Postgres DDL (Section 7 of the build plan)
etl/                    currency/date parsers + unit tests, SQLite->Postgres ETL
api/                    FastAPI app (server-side scoring only)
frontend/               Next.js App Router UI (renders only, never scores)
scripts/                download/verify, schema apply, data profiling
docs/                   data caveats, deck outline
data/raw/               downloaded SQLite dumps (gitignored, not committed)
```

## Setup

### Data

```
python scripts/download_verify.py aoc_tenders
python scripts/download_verify.py tenders_vps
python scripts/inspect_schema.py data/raw/aoc_tenders.db
```

### Database

Postgres connection string goes in `.env` (copy from `.env.example`).
This build uses a cloud Postgres instance (Neon/Supabase free tier) since
the dev environment has no local Postgres/Docker.

```
python scripts/apply_schema.py
```

### API

```
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```
cd frontend
npm install
npm run dev
```

## Status

See `MHASH26-BUILD-PLAN.md` Section 11 for the hour-by-hour schedule
(H0-H6, H6-H18, H18-H30, H30-H40, H40-H48) and check progress against
that rather than inventing a new plan.
