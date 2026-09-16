# Project status

**As of:** 2026-09-16 19:16 IST, **about H+18.7**. H0 is the first commit
(2026-09-16 00:33 IST). Plan H+48 is about 2026-09-18 00:30 IST. The
submission closes at the end of 17 September, so the last hour is gone.

**Schedule position:** start of the **H18–H30** block (scoring, back-test,
polish). Feature freeze is at **H+30, about 2026-09-17 06:30 IST**.

**Summary.** The engineering spine is **ahead of schedule on code** but
**behind on the checks that matter**. All code through H18–H30 exists: six
flags, scoring, API, three screens, triage and the synthetic back-test
harness. But **no real-slice numbers are confirmed**, the back-test result
in the repo comes from the dev fixture, nothing is deployed, and the
business half (deck, video, verification of the 2026 claims) has barely
started.

Checked by reading the code and running tests on this machine. This
machine has no `data/raw/` dumps, no `.env` and no running Postgres
(Docker daemon is not up), so **nothing database-backed was executed
here**.

---

## Block-by-block against Section 11

### H0–H6: prove the data, then commit ✅ done

| Role | Deliverable | Status | Evidence |
|---|---|---|---|
| D | Download dump, verify SHA-256 | ✅ | `scripts/download_verify.py`, checksums pinned |
| D | H+4 gate: is `Number of bids received` populated? | ✅ **98.8% populated** (1.2% null in a 20k sample) | `docs/h4-data-report.md` |
| L | Assam/APHCL query, back-test decision by H+10 | ✅ **Not in corpus → synthetic fallback** | `docs/h4-data-report.md` |
| E | Repo, Postgres, schema | ✅ | `db/schema.sql`, `scripts/apply_schema.py` |
| F | Next.js scaffold, detail card on fake JSON | ✅ | `frontend/src/app/awards/demo`, `lib/fakeData.ts` |
| P | Read official M#26 template, skeleton deck | ⚠️ **Partial.** Outline only; `docs/deck-outline.md` says nobody has fetched the official template | `docs/deck-outline.md` |

Slice decision: **six Coal India subsidiaries, 2019–2025, about 140k
awards, 98.8% joined to notices** through the base64-decoded `tender_id`
key. This replaced the first choice, Madhya Pradesh, which joined only 0.4%.

### H6–H18: ingest and first flags ✅ code done / ⚠️ real run unconfirmed

| Role | Deliverable | Status | Notes |
|---|---|---|---|
| D | SQLite → Postgres ETL | ✅ code | `scripts/etl_load.py`. `docs/etl-reject-report.md` shows a real run (138,512 rows) happened on some machine |
| D | Currency and date parsers with unit tests | ✅ | **70 tests pass** (`pytest etl/tests api/tests`) |
| D | Reject log | ✅ | Written to `docs/etl-reject-report.md`. See risk R4: it reports 0 rejects |
| E | F1, F2, F5, F9, F11, F12 as SQL, each with `evidence` | ✅ | `scripts/compute_flags.py`. All thresholds read from YAML |
| F | Real card, list view, filters wired to API | ✅ | `/awards`, `AwardFilters.tsx`, `lib/api.ts` |
| P | Slides 1–4 | ❌ **Not started** (outline only) | |

**Definition of done** was "flags run over the loaded slice and produce
rows in `flag`." **We can't confirm this for the real slice.** Nothing in
the repo records flag counts from a real-slice run.

### H18–H30: scoring, back-test, polish 🟡 current block

| Role | Deliverable | Status | Notes |
|---|---|---|---|
| E | Weights YAML, composite score, ranking | ✅ | `config/weights.yaml`, `scripts/compute_scores.py`, dense rank within the slice only |
| L+D | **Run the back-test, produce the number** | ⚠️ **Harness done, real number missing** | `docs/backtest-report.md` shows 13/13 planted awards, worst rank #14 of 3,665. **Per the README these numbers came from the dev fixture** (8k synthetic awards), not the real CCL history. **Must be re-run on the real slice.** |
| F | Explanation panel from `evidence` | ✅ | `DetailCard.tsx`, `FlagRow.tsx`, sentences from `api/app/explain.py` (deterministic templates, no LLM) |
| F | Triage control | ✅ | `PUT /awards/{id}/review`, `TriageControl.tsx` |
| F | Organisation summary screen | ✅ | `/organisations/[id]`, `GET /organisations/{id}/summary` |
| P | Monetisation and marketing slides **finished** | ❌ **Not started** | Plan says start with monetisation |

**Definition of done** was "the number exists and the explanation panel
renders real evidence." **Not met:** the only number is from the fixture,
and no real evidence has been rendered on this machine.

### H30–H40: freeze, deploy, rehearse ❌ not started

- ❌ Deployment to a single box. No Dockerfile, Compose file or Render/Railway config in the repo.
- ❌ A seeded known-good demo state (exact filters and exact award for camera).
- 🟡 Empty states: the ranked list has one ("No awards match these filters"). **No loading states** found (`loading.tsx` / loading UI).
- ❌ Legibility pass at video resolution.
- ❌ Video script.
- ✅ Synthetic-data banner (`SyntheticBanner.tsx`, driven by `/meta/dataset`).
- ✅ `/awards/demo` works with no backend, as a fallback.

### H40–H48: video and submission ❌ not started

---

## Section 5 scope check

| In-scope component | Status |
|---|---|
| Slice ingest, SQLite → Postgres | ✅ code, ⚠️ not re-run here |
| Currency and date parsers with tests | ✅ |
| Six deterministic SQL flags | ✅ |
| Weighted score from YAML | ✅ |
| Ranked list and detail page | ✅ |
| Explanation card with real numbers | ✅ code, ⚠️ not shown on real data |
| Triage states | ✅ |
| Back-test | ⚠️ synthetic fallback built, real-slice number pending |

**Out-of-scope creep:** none found. No entity resolution, graph, LLM, Neo4j,
Kafka or auth.

## Section 13 rule compliance

| Rule | Status | Finding |
|---|---|---|
| 1 Scope | ✅ | |
| 2 No LLM in scoring | ✅ | No LLM anywhere; sentences are templates |
| 3 Every flag writes evidence | ✅ | All six `jsonb_build_object` |
| 4 Thresholds only in YAML | ⚠️ | **`api/app/main.py` organisation summary hardcodes the late-March window** (`MONTH = 3`, `DAY >= 18`, baseline `14/365`) instead of reading `F12_YEAR_END_RUSH`. F1's `'%open%'` pattern is also inline in `compute_flags.py`. Frontend score colour bands (`>= 1.8`, `>= 1.0` in `awards/page.tsx`) are display-only but are still magic numbers |
| 5 Server-side scoring | ✅ | Frontend only renders |
| 6 Parser tests before use | ✅ | |
| 7 No identity claims | ✅ | Org summary returns an explicit exact-name caveat |
| 8 No new deps | ✅ | Stack as specified |
| 9 Narrow over general | ✅ | |
| 10 No synthesised values | ✅ | Fixture is sentinel-marked, bannered and refuses to overwrite real data. See R3 on the back-test report wording |

---

## Open risks and gaps, in priority order

| # | Risk / gap | Impact | Action | Owner |
|---|---|---|---|---|
| R1 | **Back-test number came from the fixture, not the real slice** | The deck's key slide has no defensible number | Load the real slice, run flags → scores → `backtest_synthetic.py`, commit the new report | L+D |
| R2 | **F1 relies on `tender_type ILIKE '%open%'`, but the real `Tender Type` mixes category values (`Works/Goods/Services`) with mode values** (h4 report). The ETL does not normalise it | F1, the headline flag, may fire far less often on real data than on the fixture | After the real load, count `tender_type` values and F1 hits. If coverage is low, report it plainly (rule 10) or decide on normalisation and **ask before changing scope** | E |
| R3 | `docs/backtest-report.md` names **Central Coalfields Limited** and calls it a "real history", but the rows were fixture data using real PSU names | A reader may take fixture results as real CCL results | Re-run on real data (fixes it), or add a line saying the numbers come from the dev fixture | L |
| R4 | ETL reject report shows **0 currency and 0 date rejects in 138,512 rows**. Also, `etl_load.py` silently `continue`s on bad `details_json` and swallows a bad `bids_received` int | Either the data is clean or rejects are going unlogged, which is exactly what rule 6 warns about | Spot-check null counts of `contract_value`, `contract_date` and `bids_received` in Postgres against 138,512 | D |
| R5 | F5 citation is always "GFR 2017 Rule 162", even for the Rs 5 lakh (Rule 155) and Rs 50,000 (Rule 154) thresholds. The correct rule is already in `evidence.rule` | A wrong legal citation on the card is a credibility hit | Use `evidence.rule` in `explain.py` | E |
| R6 | Rule 4 violation in the org summary (hardcoded March window) | Changing YAML would make the org screen disagree with F12 | Read from `get_weights()` | E |
| R7 | No deploy setup | The demo depends on a laptop (plan forbids this) | Compose or Render/Railway by H+40 | L |
| R8 | No loading states | Section 10 non-negotiable | Add `loading.tsx` per route | F |
| R9 | **Deck, video and business slides not started**. Official template not read | Two of six Round 1 criteria are business criteria | P starts on monetisation now | P |
| R10 | The three 2026 claims (CAG May 2026, CCI 7 Apr 2026 Rs 7.56 cr, CPPP figures) have no verification record | A wrong public-record claim is "unusually expensive" (Section 4) | One person opens every Section 18 link and records the result here | P |
| R11 | Plan Section 6 requires a **first-party minimal scraper** in the repo, "actually works against at least one organisation". None exists | Dependence on the mirror host. Can't claim it in deck | Build a minimal one after freeze-critical work, or drop the claim from the deck | D |
| R12 | Fixture uses real PSU names with fake awards | Screenshots taken from a fixture DB could look like findings | Banner covers the UI. Never capture deck or video from the fixture DB | F/P |

## Section 15 submission checklist

- [ ] Official M#26 template, PDF
- [ ] Filename `TeamID_TeamName_ProblemStatementID`
- [ ] No institute name, logo or identifiable background
- [ ] All five members on camera
- [ ] Video ≤ 3 min (prototype)
- [ ] First two minutes stand alone
- [ ] GitHub repo public, checked from incognito on mobile data
- [ ] Vendor names redacted in all artefacts
- [ ] CAG, CCI and CPPP 2026 claims verified against source
- [ ] Submitted with hours to spare

## Section 17 open questions

1. Which slice? ✅ **Resolved:** Coal India subsidiaries 2019–2025.
2. Open-source the flag library at Round 1? ❓ No decision recorded.
3. Journalist or audit-firm contact? ❓ No record.
4. Who records and edits the video? ❓ **Unassigned** (plan says assign at H0).

## Next 12 hours (to feature freeze at H+30)

1. **L+D:** load the real slice into a reachable Postgres, then run `compute_flags.py` → `compute_scores.py` → `backtest_synthetic.py`. Commit the reports. (R1, R3, R4)
2. **E:** check F1 coverage on real data (R2). Fix F5 citation (R5) and org-summary hardcoding (R6).
3. **F:** loading states (R8). Legibility pass once real data renders.
4. **P:** read the official template. Monetisation slide, then slides 1–4. Verify the three 2026 claims (R10, R9).
5. **L:** pick the deploy target now so H30–H40 is deploy, not decisions (R7). Assign the video owner.

## Verified on this machine

- `python -m pytest etl/tests api/tests -q` → **70 passed**
- Frontend: `npm ci` ✅, `npm run lint` ✅ (clean), `npm run build` ✅. All six routes compile: `/`, `/awards`, `/awards/[id]`, `/awards/demo`, `/organisations/[id]`. Bare `tsc --noEmit` complains about `PageProps`/`LayoutProps`, but those are Next 16 route types that `next build` generates, and its own TypeScript step passes.
- Node is v22.11.0, and one lint dependency asks for ≥22.13. It's only a warning, but pin the Node version on the deploy box.
- Not runnable here: ETL, flags, scores, back-test, API against a DB (no dumps, no `.env`, Docker daemon down)
