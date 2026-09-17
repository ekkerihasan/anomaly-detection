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

Loaded slice: six Coal India Limited subsidiaries, 2019–2025, ~140k award
rows, 98.8% joinable to notice-side data. See `docs/h4-data-report.md` for
how that slice was chosen and why the obvious candidates were rejected.

## Layout

```
config/weights.yaml    flag weights & thresholds (never hardcoded elsewhere)
db/schema.sql          Postgres DDL (Section 7 of the build plan)
etl/                   currency/date parsers + unit tests
api/                   FastAPI app (reads precomputed flags/scores) + tests
frontend/              Next.js App Router UI (renders only, never scores)
scripts/               pipeline: download, schema, ETL, flags, scores, back-test
docs/                  data caveats, deck outline, data + back-test reports
data/raw/              downloaded SQLite dumps (gitignored, not committed)
```

## Pipeline order

Each step depends on the one before it:

```
scripts/download_verify.py   fetch + SHA-256 verify the mirror dumps
scripts/apply_schema.py      create tables (one-shot DDL, no migration tool)
scripts/etl_load.py          SQLite -> Postgres for the chosen slice
scripts/compute_flags.py     six deterministic SQL flags -> flag table
scripts/compute_scores.py    weighted composite score + rank -> risk_score
scripts/backtest_synthetic.py  synthetic injection back-test (Section 9)
```

`compute_flags.py` and `compute_scores.py` are re-runnable and idempotent —
each truncates its own output table first.

## Setup

### Database

Connection string goes in `.env` (copy from `.env.example`).

Either a cloud Postgres instance (Neon/Supabase free tier), or a local one
via Docker:

```
docker run -d --name mhash-pg \
  -e POSTGRES_PASSWORD=devpass -e POSTGRES_USER=dev -e POSTGRES_DB=procurement \
  -p 55432:5432 postgres:16-alpine

# .env
DATABASE_URL=postgresql://dev:devpass@localhost:55432/procurement
```

Then:

```
python scripts/apply_schema.py
```

### Working without the real slice

The full ETL needs multi-GB dumps. To develop the engine, API and UI
without them, seed a synthetic fixture into the real schema:

```
python scripts/seed_dev.py --awards 8000
python scripts/compute_flags.py
python scripts/compute_scores.py
```

**Everything this generates is fake.** The fixture marks its organisations
with a sentinel `org_type`, `/meta/dataset` reports `synthetic: true`, and
every page renders a persistent amber "SYNTHETIC DEV FIXTURE" banner. Load
a real slice and the banner disappears on its own — there is no flag to
remember to unset (CLAUDE.md rule 10).

`seed_dev.py` refuses to run if the database contains any non-fixture
organisation, so it cannot clobber a real load.

### API

```
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Routes: `/awards` (ranked list, filterable), `/awards/{id}` (detail with
flags, evidence, generated sentences), `PUT /awards/{id}/review` (triage),
`/organisations`, `/organisations/{id}/summary`, `/config/weights`,
`/meta/dataset`, `/health`.

### Frontend

```
cd frontend
npm install
npm run dev
```

Screens: `/awards` ranked queue, `/awards/{id}` explanation card,
`/organisations/{id}` summary, `/awards/demo` design reference (renders
with no database or API — the fallback if the demo box loses its backend).

Use **http://localhost:3000**. Next 16 blocks cross-origin dev resources,
so other hostnames can leave client components rendered but not hydrated —
`allowedDevOrigins` in `next.config.ts` covers `127.0.0.1` as well.

## Tests

```
python -m pytest etl/tests api/tests -q
```

Covers the currency and date parsers (CLAUDE.md rule 6) and the flag →
sentence templates, including that an incomplete `evidence` blob degrades
to an honest message rather than rendering "None" at an auditor.

## Back-test

The Assam Police Housing Corporation tenders are not in this corpus
(`docs/h4-data-report.md` records the search). Section 9's disclosed
fallback is implemented instead:

```
python scripts/backtest_synthetic.py            # inject, score, report
python scripts/backtest_synthetic.py --cleanup  # remove planted rows
```

It plants demand-splitting and bid-rotation patterns into the largest
organisation's history, re-runs the **unmodified** engine, and reports
precision/recall at review budget K. Results land in
`docs/backtest-report.md`, labelled synthetic. Re-run it against the real
slice once that is loaded — the committed numbers are from the dev fixture
and are not a claim about real data.

## Status

See `MHASH26-BUILD-PLAN.md` Section 11 for the hour-by-hour schedule
(H0-H6, H6-H18, H18-H30, H30-H40, H40-H48) and check progress against
that rather than inventing a new plan.

Done: schema, parsers + tests, ETL, six flags with evidence blobs,
composite scoring and ranking, full API, all three screens, triage
persistence, synthetic back-test harness — **and the real slice is now
loaded and scored**: 138,512 awards / 131,048 with at least one flag,
166,047 flag rows, scores ranging 0.16-2.45. The synthetic back-test
(`docs/backtest-report.md`) has been re-run against this real
population: 13/13 planted awards detected, worst-ranked at #19 of
131,061 (top 0.01%).

Not done: deploy, deck, video.

Note on F2_SHORT_WINDOW: ~92% of awards in this slice carry this flag —
checked against raw dates (not a parsing bug): the bulk of "Open/
Advertised" e-tenders in this corpus run ~10-11 day bid windows against
GFR Rule 161's 21-day minimum. This looks like a real, sector-wide
finding rather than noise; the severity gradient (1.0 at <=7 days down
to 0.3 at 20 days) still differentiates within that population, and the
composite score pulls in the other five flags on top of it.
