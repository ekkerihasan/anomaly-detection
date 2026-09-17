# Project status

**As of:** 2026-09-17 17:24 IST, **about H+40.8**. H0 is the first commit
(2026-09-16 00:33 IST). Submission closes at **end of 17 September, about
6.5 hours from now**. The plan's H+48 (about 18 Sep 00:30) is past the
deadline, so there is no slack.

**Schedule position:** **H40–H48, video and submission**. Feature freeze
(H+30, 17 Sep 06:30) has passed.

**Since the last report** (commit `60719de`, 16 Sep 19:27):

- `1f1dee8` (Abubaker, 17 Sep 00:57): **the real slice is loaded and
  scored**, and the synthetic back-test was re-run on it. Only docs were
  changed (`README.md`, `docs/backtest-report.md`).
- `633db15`: merge from `origin/main`.
- **Uncommitted, this session (17 Sep ~17:40):** R5 (F5 citation) and R6
  (org summary March window hardcoded) are **fixed in the working tree**.
  Tests: **72 passed** (2 new). **Not run against the real DB**, because
  this machine has none. Re-check `/awards/{id}` and
  `/organisations/{id}/summary` on the DB machine before recording.
- **Uncommitted, demo-critical frontend pass (17 Sep ~18:00):**
  - Loading states on all three screens (R8)
  - `REDACT_VENDORS=1` display switch for recordings (R13)
  - Organisation names shown as `Central Coalfields Limited · Kathara` instead of `||`
  - Null guards on the detail card (a missing date or value no longer renders as `01 Jan 1970` or `₹0`)
  - Ranked-list copy no longer says "queue, not a scoreboard" (Finding 1)
  - Readable rule citation (`Basis: …`, `text-sm`)

  Lint and build pass. Checked on a dev server using `/awards/demo` and
  `/awards` with no API: redaction shows `Vendor BC14BC`, the real name is
  absent from the HTML payload, and the loading and API-unreachable states
  render.

**Summary.** The engine now runs end to end on real data: **138,512
awards, 166,047 flag rows, 131,048 awards with at least one flag, scores
0.16–2.45**. The back-test finds 13/13 planted awards, the worst at dense
rank #19 of 131,061. Engineering is mostly done, but **deploy and the
whole pitch half (deck, video, claim checks, submission) have no trace in
this repo** with 6.5 hours left.

---

## How much is left

**About 51% of the Round 1 deliverable is left**, weighted by what the plan
says scores (Section 2: two of six criteria are business, plus a
prototype bonus).

| Area | Weight | Done | Left | Basis |
|---|---:|---:|---:|---|
| Engineering (data, ETL, flags, scoring, API, screens, polish, deploy) | 47 | 40 | 7 | Deploy (5), scraper (2) not done. Citation/threshold fixes, loading states, legibility and redaction done (uncommitted) |
| Back-test | 10 | 8 | 2 | Real-slice run done. K table needs confirming as regenerated output (R3) |
| Pitch and submission (deck, monetisation/marketing, claim checks, video script, recording, upload) | 43 | 1 | 42 | Only `docs/deck-outline.md` exists |
| **Total** | **100** | **49** | **51** | |

**Caveat:** this counts only what is visible in the repo. If the deck or
video is being made elsewhere (Google Slides, Canva, a phone), the pitch
figure is understated. Update this table once P reports.

At this point the ~51% left is almost all **pitch and submission work**,
not code. Engineering is about 85% done. The pitch half is about 2% done.

---

## Block-by-block against Section 11

### H0–H6: prove the data, then commit ✅ done

| Role | Deliverable | Status |
|---|---|---|
| D | Download, verify SHA-256 | ✅ `scripts/download_verify.py` |
| D | H+4 gate: `Number of bids received` populated? | ✅ 98.8% populated |
| L | Assam/APHCL search, decide by H+10 | ✅ Not in corpus → synthetic fallback |
| E | Repo, Postgres, schema | ✅ |
| F | Next.js scaffold, detail card on fake JSON | ✅ |
| P | Read official M#26 template, skeleton deck | ⚠️ Outline only; template still not recorded as read |

### H6–H18: ingest and first flags ✅ done

| Role | Deliverable | Status |
|---|---|---|
| D | ETL SQLite → Postgres | ✅ **Real slice loaded**: 138,512 awards |
| D | Currency and date parsers with tests, reject log | ✅ 70 tests pass. Reject log shows 0 rejects (R4) |
| E | Six flags with `evidence` | ✅ 166,047 flag rows on real data |
| F | Card, list, filters wired to API | ✅ |
| P | Slides 1–4 | ❌ No trace in repo |

**Definition of done** ("flags run over the loaded slice and produce rows
in `flag`"): **met.**

### H18–H30: scoring, back-test, polish 🟡 engineering met, pitch not

| Role | Deliverable | Status |
|---|---|---|
| E | Weights YAML, composite score, ranking | ✅ Real slice scored, 0.16–2.45 |
| L+D | **Back-test number** | ✅ **13/13 planted awards found, worst #19 of 131,061 (top 0.01%)**, synthetic injection on real CCL history. See R3 |
| F | Explanation panel, triage, org summary | ✅ |
| P | Monetisation and marketing slides finished | ❌ No trace in repo |

**Definition of done** ("the number exists and the explanation panel
renders real evidence"): **number exists.** Nothing in the repo records
the panel rendering real evidence, so confirm it in the demo run.

### H30–H40: freeze, deploy, rehearse ❌ missed

- ❌ Single-box deploy. No Dockerfile, Compose or Render/Railway config. **The demo still depends on a laptop.**
- ❌ Seeded known-good demo state (exact filters and exact award on camera)
- ✅ Loading states on all three screens (uncommitted). Ranked list has an empty state and an API-unreachable state
- 🟡 Legibility pass: citation enlarged, null values guarded, org names cleaned. **Still to do:** view at recording resolution on real data
- ❌ Video script
- ✅ Synthetic banner. `/awards/demo` works with no backend as a fallback

**Definition of done** ("the demo runs end to end from a URL, twice,
without intervention"): **not met.**

### H40–H48: video and submission ❌ current block, not started

- ❌ Recording (all five on camera; screen capture separate from talking heads)
- ❌ Edit to ≤ 3 min, with the first 2 min standing alone
- ❌ Submission

---

## Findings on the real-slice results

1. **F2_SHORT_WINDOW flags about 92% of awards**, and 94.6% of all awards
   now have at least one flag (131,048 of 138,512). The README says this was
   checked against raw dates and is a real sector pattern: bid windows of
   about 10–11 days against a 21-day rule. Even if that holds, **the
   "review queue, not a scoreboard" line in the UI and pitch no longer
   holds**, since nearly every award is in the queue. The ranking still
   separates awards (top 0.01% for planted rows). **Pitch it as a finding**
   ("most advertised tenders in this slice ran about half the GFR minimum
   window") and make the pitch lean on rank, not on whether an award is
   flagged.
2. **"Organisation" means a mining area, not a subsidiary.** The back-test
   host is `Central Coalfields Limited||Kathara`. The raw `org_name`
   carries a sub-unit suffix, and the ETL keeps it. The org summary screen
   and any "largest organisation" claim are therefore area-level. Say so,
   or strip the suffix in display.
3. **Per-flag counts aren't recorded anywhere.** We know the F2 share but
   not how many F1 (single-bid) flags fired. F1 is the headline flag and
   depends on the messy `tender_type` field (R2). Run
   `SELECT code, count(*) FROM flag GROUP BY code` and record it here
   before any slide quotes flag numbers.

---

## Open risks and gaps, in priority order (for the ~6.5 hours left)

| # | Risk / gap | Status | Action | Owner |
|---|---|---|---|---|
| R9 | **Deck, monetisation/marketing slides, video not in repo**. Official template not recorded as read | ❌ open, **critical** | P reports what exists. If nothing: template → monetisation → problem/results slides, now | P |
| R7 | **No deploy**. Demo depends on a laptop | ❌ open, **critical** | For a recorded video, a local run is acceptable. Record the screen capture from a known-good local state first; deploy only if time allows | L |
| R10 | The three 2026 claims (CAG, CCI Rs 7.56 cr / 7 Apr 2026, CPPP figures) are unverified | ❌ open | Open each Section 18 link and record the result here before slides are exported | P |
| R3 | Back-test report: header lines were hand-edited for the real run, but **the K table is byte-identical to the fixture run**. That's possible, but unconfirmed | ⚠️ partly resolved | Re-run `scripts/backtest_synthetic.py` and commit its generated report unedited, so the slide number is reproducible | L |
| R2 | F1 relies on `tender_type ILIKE '%open%'` over a mixed field. F1 hit count on the real slice is unknown | ❌ open | Record per-flag counts (Finding 3). If F1 is low, say so on the data-limits slide | E |
| R5 | F5 citation was always "GFR 2017 Rule 162", even at the Rs 5 lakh (Rule 155) and Rs 50,000 (Rule 154) thresholds | ✅ **fixed, uncommitted** | `explain.py` now cites `evidence.rule` (copied from YAML by `compute_flags.py`), with tests for 155 and 154. No flag recompute needed; the rule is already in stored evidence | E |
| R6 | Org summary hardcoded the March window and `14 / 365`, a rule 4 breach | ✅ **fixed, uncommitted** | `main.py` reads `month`/`day_from` from `F12_YEAR_END_RUSH`, and the baseline uses the same arithmetic as `compute_flags.py` (still 14/365 with current YAML, so numbers on screen are unchanged) | E |
| R8 | No loading states | ✅ **fixed, uncommitted** | `loading.tsx` for `/awards`, `/awards/[id]`, `/organisations/[id]` | F |
| R1 | Back-test number came from the fixture | ✅ **resolved** | Re-run on real slice | |
| R4 | 0 currency and 0 date rejects in 138,512 rows. ETL silently skips bad `details_json` and bad bid counts | ⚠️ open, low priority now | Post-submission | D |
| R11 | No first-party scraper (Section 6) | ❌ open | **Drop the claim from the deck**; not worth building in the last hours | D/P |
| R12 | Fixture uses real PSU names | ⚠️ low | Never capture from the fixture DB; real slice is loaded now | F/P |
| R13 | Vendor names on screen in recordings (Section 14) | 🟡 **mitigated, uncommitted** | Start the frontend with `REDACT_VENDORS=1` for every recording. Vendors show as stable codes (`Vendor 3F2A9C`) on list, card and org pages. **Not covered:** vendor names inside tender titles, raw API JSON, and the CPPP link target. Don't open those on camera. Display mask only: the API still returns real names | L/P |

## Section 15 submission checklist

- [ ] Official M#26 template, PDF
- [ ] Filename `TeamID_TeamName_ProblemStatementID`
- [ ] No institute name, logo or identifiable background
- [ ] All five members on camera
- [ ] Video ≤ 3 min (prototype)
- [ ] First two minutes stand alone
- [ ] GitHub repo public, checked from incognito on mobile data. **`github.com/ekkerihasan/anomaly-detection` is PUBLIC per `gh repo view` (17 Sep).** Incognito/mobile check still to do, and push the uncommitted fixes
- [ ] Vendor names redacted in all artefacts
- [ ] CAG, CCI and CPPP 2026 claims verified against source
- [ ] Submitted with hours to spare

## Section 17 open questions

1. Which slice? ✅ Coal India subsidiaries 2019–2025 (area-level orgs, see Finding 2).
2. Open-source the flag library at Round 1? ❓ No decision recorded.
3. Journalist or audit-firm contact? ❓ No record.
4. Who records and edits the video? ❓ **Still unassigned in repo.**

## Recording setup (demo-critical)

1. On the DB machine: pull, then start the API (`uvicorn app.main:app` from `api/`).
2. Start the frontend **with redaction**. In PowerShell: `$env:REDACT_VENDORS="1"; npm run dev`. In bash: `REDACT_VENDORS=1 npm run dev`. Open **http://localhost:3000** (not 127.0.0.1).
3. If using `npm run build && npm start`, set `REDACT_VENDORS=1` for **both** commands. `/awards/demo` is prerendered at build time, so it takes the build-time value.
4. Check one frame of each screen for real vendor names before recording the full take.
5. Hold the demo state as URLs (filters are query params). Write the exact `/awards?...` and `/awards/{id}` links here once chosen.

## What can be done now (freeze bypassed)

Feature freeze (H+30) has passed. Treat everything below as allowed, but
**any code change now has to be re-verified on the real DB before the
screen recording**, because a broken page on camera costs more than the fix
gains.

**Machine constraints:** this laptop has no dumps, no `.env`, no Postgres,
and the Docker daemon is not running. The real DB lives on the machine
that produced `1f1dee8`.

### A. Can be done now, on this machine (code only, no DB)

| Stage (plan block) | Item | Effort | Worth it before submission? |
|---|---|---|---|
| H30–H40 F | **Loading states** (R8) | done | ✅ Done, uncommitted |
| H30–H40 F | **Vendor redaction for recordings** (R13) | done | ✅ Done, uncommitted |
| H30–H40 L | **Deploy config** (Dockerfile for API and frontend, `docker-compose.yml` with Postgres) (R7) | ~45 min to write | **Maybe.** Can't be tested here unless Docker Desktop is started. The video doesn't need it; the "runs from a URL" claim does |
| H6–H18 D | ETL reject logging for skipped `details_json` and bad `bids_received` (R4) | ~15 min | **No, not before submission.** Only matters after a re-load, and re-loading the slice now is a risk |
| Section 6 D | First-party scraper, working against one organisation (R11) | 1–2 h, network-dependent | **No.** Drop the claim from the deck instead |
| H30–H40 F | Legibility pass (font sizes, number contrast) | done here | 🟡 Done for what's checkable without data. Final look at recording resolution needs real data |

### B. Can be done now, but only on the DB machine

| Stage | Item | Why it can't run here |
|---|---|---|
| H18–H30 E | Per-flag counts on the real slice (Finding 3), F1 coverage check (R2) | needs Postgres |
| H18–H30 L+D | Re-run `backtest_synthetic.py`, commit its unedited report (R3) | needs Postgres |
| H30–H40 L | Verify R5/R6 fixes render on real data, seed a known-good demo state, pick the on-camera award | needs API + DB |
| H40–H48 | Screen-record the Section 16 script (twice) | needs the running app with real data |

### C. Needs a decision first (ask, don't assume)

| Item | Decision |
|---|---|
| F1 `tender_type` normalisation (R2) | Changing flag logic this late changes every score and the back-test. Recommend: **don't**. Report the F1 count honestly |
| Organisation `||Area` suffix (Finding 2) | ✅ Display-only formatting applied (`Name · Area`). Grouping unchanged. Still say "mining area" on screen |
| F2 flagging ~92% of awards (Finding 1) | Framing only: pitch it as a finding, lean on rank |

### D. Human / non-code (can start right now, in parallel)

- Read the official M#26 template. Deck: monetisation → problem → results → data limits (R9)
- Verify the CAG, CCI and CPPP 2026 claims against Section 18 links (R10)
- Assign video editor; write the 3-minute script to the second
- Talking-head recordings (don't depend on the app)

## Remaining ~6.5 hours, suggested order

1. **Now, P + L:** confirm what deck/video material exists outside the repo. Assign the video editor. Read the official template.
2. **Now, E (≤30 min):** commit and push the R5/R6 fixes, pull them on the DB machine, check the two affected pages. Record per-flag counts (Finding 3). Re-run the back-test and commit its generated output (R3). These feed the slides.
3. **P:** monetisation slide, results slide (13/13, #19 of 131,061, labelled **synthetic injection on real data**), data-limits slide (include the F2 92% finding and the Assam absence). Verify the 2026 claims (R10).
4. **L + F:** set up a known-good local demo state, redact vendor names, screen-record the Section 16 script twice.
5. **All:** talking heads, edit, export PDF, public repo check, **submit with at least 2 hours to spare**. Deploy (R7) only if everything above is done.

## Verified on this machine

- 16 Sep: `python -m pytest etl/tests api/tests -q` → 70 passed. Frontend `npm run lint` and `npm run build` → pass.
- 17 Sep ~17:40: after the R5/R6 fixes, `pytest etl/tests api/tests -q` → **72 passed**, and `app.main` imports cleanly. The SQL change in `/organisations/{id}/summary` was **not executed** (no DB). Frontend untouched, so the 16 Sep build result still applies.
- 17 Sep: `gh repo view` → repo is **PUBLIC**.
- 17 Sep ~18:00: frontend `npm run lint` ✅, `npm run build` ✅ after the demo pass. Dev server with `REDACT_VENDORS=1`: `/awards/demo` shows the redacted vendor code, with 0 occurrences of the real sample name in the response. `/awards` with no API shows the API-unreachable state. **Not checked against real data** (no API or DB here). Real-slice figures above come from the README and back-test report committed in `1f1dee8`. **They were not re-run here** (no dumps or `.env` on this machine).
