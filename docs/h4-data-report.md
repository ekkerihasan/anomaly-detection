# H+4 data report and back-test decision

Per MHASH26-BUILD-PLAN.md Section 11 (H0-H6 block). Produced against the
verified `aoc_tenders.db` mirror (SHA-256 matched, see
`data/raw/aoc_tenders.verified`).

## Corpus shape

`aoc_tenders.db` has three tables:

- `aoc_tenders` (4,921,960 rows) — list-level metadata: `internal_id`,
  `portal_type` (`central` | `state`), `year`, `org_name`, `ref_no`,
  `tender_id`, `aoc_date`, `closing_date`, `detail_url`.
- `aoc_details` (4,540,739 rows) — one `details_json` blob per
  `internal_id`, keyed by `aoc_tenders.internal_id`. This is where the
  actual structured fields live (Contract Value, Contract Date, Number of
  bids received, etc.) — the plan's "parse JSON detail blobs into
  columns" step (H6-H18) targets this table.
- `aoc_list_queue` — scraper bookkeeping, not used downstream.

`portal_type` splits 2,005,258 central / 2,916,702 state.

## H+4 gate: is `Number of bids received` populated?

**Yes.** Sampled 20,000 random rows from `aoc_details`:

- Field present in the JSON: 20,000/20,000 (100%)
- Null-like (`None`/`""`/`"NA"`/`"N/A"`/`"-"`): 239/20,000 (1.2%)

No pivot to notice-side-only flags is needed. F1_SINGLE_BID is viable.

**Caveat found while sampling:** the `Tender Type` field is inconsistent
— some records carry procurement *category* values (`Works`, `Goods`,
`Services`), others carry competition *mode* values (`Open`, `Limited`,
`Single`, `Nomination`, and case/spelling variants like `LIMITED`,
`Open Tender`). F1's `tender_type ILIKE '%open%'` filter will only match
the latter flavor. This needs a real decision during ETL (H6-H18) — likely
normalizing tender type into an explicit competition-mode column rather
than pattern-matching the raw string — but does not block Phase 1.

**Contract Value format caveat:** in this dump, `Contract Value` is
overwhelmingly plain numeric strings (`"194577"`, `"1003785.25"`), not the
comma-grouped/`Rs.`-prefixed forms CLAUDE.md's rule 6 describes as
possible. The currency parser (`etl/parsers/currency.py`) already handles
both — plain numeric and grouped/prefixed/lakh-crore — so no rework
needed, but the reject-log step during real ETL should report the actual
observed distribution rather than assuming the documented shapes are
representative.

## Back-test decision (Section 9)

**Searched for Assam Police Housing Corporation Limited tenders — not
found.** Checked `org_name` in `aoc_tenders` (both `central` and `state`
portal types) for `%Police Housing%`, `%APHCL%`, and `%Housing Corp%`:
zero matches for APHCL specifically (29 unrelated "Housing Corp" matches,
all Central Warehousing Corporation). 26,991 rows exist for org names
containing "Assam", none of them APHCL or electrification-related.

**Decision: synthetic injection fallback**, per Section 9's explicit
instruction ("do not fake it... take a clean organisation's real award
history, programmatically inject a splitting pattern and a rotation
pattern, report precision-at-K, and say explicitly on screen that it is
synthetic"). This must be visibly disclosed as synthetic everywhere it
appears (UI, deck, video) — CLAUDE.md rule 10.

This is decided within the H+10 deadline the plan sets.

## Slice decision

Target: one state, 5 financial years, 100k-300k award rows, good field
coverage (Section 6/11).

State-level row counts (`portal_type='state'`, all years available):
West Bengal 785,197; Maharashtra 537,695; Kerala 358,799; **Madhya
Pradesh 248,689**; Haryana 162,327; Uttar Pradesh 151,213; Tamil Nadu
139,936; Punjab 133,675; Odisha 116,148.

Per-year counts for 2021-2025 (chosen as the 5-year window — 2026 is the
current, incomplete year):

| State | 2021 | 2022 | 2023 | 2024 | 2025 | Total |
|---|---|---|---|---|---|---|
| **Madhya Pradesh** | 31,120 | 36,971 | 47,774 | 34,829 | 21,585 | **172,279** |
| Haryana | 22,566 | 20,857 | 34,516 | 27,943 | 24,842 | 130,724 |
| Tamil Nadu | 2,521 | 7,681 | 23,038 | 35,156 | 45,898 | 114,294 |
| Punjab | 24,692 | 7,688 | 16,938 | 15,689 | 22,059 | 87,066 |
| Odisha | 8,588 | 4,180 | 24,561 | 15,340 | 20,761 | 73,430 |

**Chosen slice: Madhya Pradesh, 2021-2025.** 172,279 award rows, squarely
inside the 100k-300k target, most consistent year-over-year distribution
of the candidates (no single-year collapse the way Tamil Nadu or Punjab
show), and **100% of those rows have a matching `aoc_details.details_json`
row** (verified by join, not assumed).

## Still open

- `tenders_vps.db` (notice-side: EMD, tender fee, bid window dates) not
  yet downloaded — queued next, sequential download->verify->extract->
  delete per the agreed disk strategy.
- Postgres schema not yet applied — blocked on a working `DATABASE_URL`
  (Supabase's direct-connection host is IPv6-only; this sandbox has no
  IPv6 route, so the pooler connection string is needed instead).
