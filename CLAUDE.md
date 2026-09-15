# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

M#26 hackathon Round 1 build: an automated public procurement anomaly detection tool. It ranks government tender awards by how much they deviate from normal procurement behaviour and shows an auditor *why*, so scarce human review time lands on the tenders most worth reading. Domain: Smart Governance and Compliance, SDG 16. Full plan, rationale, schedule and business strategy live in `MHASH26-BUILD-PLAN.md` — read it before making any scope or architecture decision not covered below.

No code exists yet at the time of writing; this file and the build plan are the only repo contents. As the pipeline, API, and frontend get scaffolded, update the Commands section below with real build/lint/test/run invocations.

## Rules that override default instincts (Section 13 of the build plan)

These are binding, not suggestions:

1. **Scope is fixed to the "In scope" table in Section 5 of the build plan.** Do not build anything in the "Out of scope" list no matter how easy it looks: entity resolution, fuzzy vendor matching, vendor graph/Louvain clustering, award rotation detection, peer-group percentiles, Benford's law, live CPPP pulls, GeM/state portal integrations, any LLM in the scoring path, Neo4j, Kafka, real auth, mobile support.
2. **No LLM in the scoring path, ever.** An LLM may only turn an already-computed flag into a plain-English sentence, and it must never influence the score. "We did not use an LLM to decide" is a stated trust feature of the product.
3. **Every flag must write an `evidence` JSON blob.** A flag implementation with no evidence output is not done — the explanation UI renders directly from this field.
4. **Weights and thresholds live in `config/weights.yaml`, never hardcoded** in a query, migration, or component.
5. **All scoring is server-side.** The frontend only renders; it never computes scores or evaluates flag logic.
6. **Currency parsing needs unit tests before anything depends on it.** Values arrive in forms like `"1,23,45,678.00"`, `"Rs. 45,00,000"`, `"NA"`, `""`, and sometimes in lakhs. Build one parser, test it against real strings pulled from the dump, and log every rejected value — a silent `None` here silently kills three flags.
7. **Never claim vendor identity.** Vendor matching is normalised exact-name match only (`vendor.name_norm`), not fuzzy/entity resolution. Language must say "possible relationship, for review", never "same entity."
8. **Stack is fixed, no new dependencies without asking:** Python, Postgres, FastAPI, Next.js (App Router, React), pandas or DuckDB for exploration. Explicitly no Neo4j, no Kafka, no ORM migration framework, no auth library.
9. **Prefer a narrow, working thing over a general framework.** This is a 48-hour build, not a platform.
10. **If the data doesn't support a feature, say so and stop.** Never synthesise values to make a screen look complete — the one exception is an explicitly-labeled synthetic back-test fallback (see Section 9 of the plan), which must be disclosed on screen as synthetic.

## Architecture (target, per the build plan)

**Pipeline:** SQLite (public CPPP mirror dump) → ETL → Postgres. The mirror is cited in the deck/README as sourced from `eprocure.gov.in`; SHA-256 of the mirror must be verified before use, and a minimal first-party scraper is kept in-repo so the pipeline isn't dependent on the third-party mirror host.

**Data slice:** Not the full corpus. One state or two-to-three ministries with good field coverage, five financial years, targeting 100k–300k award rows — chosen for query speed (sub-second on camera) and ETL time, not preference.

**Schema (Postgres, see Section 7 of the plan for full DDL):** `organisation`, `vendor`, `tender`, `award`, `flag` (code, severity 0–1, `evidence` JSONB — the load-bearing column the UI renders from), `risk_score` (award_id, score, rank), `review` (triage status: open/reviewing/referred/dismissed, note). `contract_variation` table exists in schema now but stays empty in Round 1 — it's the landing spot for Round 2 (post-award subcontractor variations), same engine reused.

**Detection engine:** Six deterministic SQL flags over `award` joined to `tender`, no entity resolution required — F1_SINGLE_BID, F2_SHORT_WINDOW, F5_THRESHOLD_BUNCHING, F9_INSTANT_AWARD, F11_EMD_ANOMALY, F12_YEAR_END_RUSH. Each has a specific legal/audit basis (GFR rules, OCP red flags) cited in Section 8 — preserve these citations in code comments/docs since they're part of the product's credibility argument. Composite score = Σ(weight[code] × severity), weights from `config/weights.yaml`, ranked within the loaded slice only (never claim a national percentile that hasn't been computed).

**Frontend:** Three screens — ranked list (filterable table), detail/explanation card (one row per flag with a plain-English sentence + real evidence numbers + rule citation, plus triage controls), organisation summary (aggregate stats: single-bid rate, concentration, value distribution, March clustering). The detail/explanation card is the highest-value component — design it early against hardcoded fake JSON before real data exists.

**Validation approach:** A back-test against the Assam Police Housing Corporation bid-rigging case (CCI order, 7 April 2026) is the single most important deliverable — it's what proves the engine works against a real, concluded cartel case. If those tenders aren't in the loaded slice, the fallback is an explicitly-disclosed synthetic injection test (inject a splitting/rotation pattern into a clean organisation's real history, report precision-at-K). Decision between real back-test vs. synthetic fallback must be made early (H+10 in the plan's timeline) since it determines what the rest of the build optimizes for.

## Data caveats to respect in code and UI copy

The CPPP data does **not** include: estimated/pre-bid value (so "award vs. estimate" flags are impossible), per-bidder prices or losing bidders' names (so classic price-based cartel screens can't be computed), PAN/GSTIN/CIN (vendor identity is free text only), or conflict-of-interest/beneficial-ownership data. These are stated as intentional, named limitations in the product's own UI/deck, not silently worked around.

## Working with the build plan document

`MHASH26-BUILD-PLAN.md` is written in H+ hours from an H0 start time and includes an hour-by-hour schedule with roles (D=data, E=engine, F=frontend, P=pitch, L=lead) and hard definitions-of-done per block. If asked to plan or sequence work, check current progress against that schedule's blocks (H0–H6, H6–H18, H18–H30, H30–H40, H40–H48) rather than inventing a new plan. If a requested feature or decision isn't covered by the plan, ask rather than assume — do not silently expand scope.
