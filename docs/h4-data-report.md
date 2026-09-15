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

## Slice decision — REVISED at start of Phase 2 (H6-H18)

The Phase 1 slice decision below (Madhya Pradesh, state government) was
**abandoned** once ETL design started and the award-side/notice-side join
was actually tested. Keeping the full investigation here rather than
quietly overwriting it, since it's exactly the kind of "coverage decides
this, not preference" call the plan asks for at H+4 — it just took until
early Phase 2 to surface the real constraint.

### The join problem

F2_SHORT_WINDOW, F9_INSTANT_AWARD, and F11_EMD_ANOMALY all need fields
that only exist on the **notice side** (`tenders_vps.db`: bid window
dates, bid opening date, EMD) joined to the **award side**
(`aoc_tenders.db` / `aoc_details`: contract date, contract value).
`aoc_tenders.ref_no` is blank on essentially every row, so the join has
to go through `aoc_details.details_json["Tender Ref. No."]` (free text)
or something better.

Free-text reference-number matching against Madhya Pradesh notices
(normalised, case/whitespace-insensitive) matched **18/5,000 sampled
award rows (0.4%)** — unusable. Checking `tenders_vps.tenders.portal_type`
explains why: `state` portal_type has only 41,825 rows nationwide (vs.
4.9M state-portal awards in `aoc_tenders`) — this mirror's notice-side
crawl barely covers state government departments at all. `org` portal_type
(3.91M rows) covers named organisations — mostly central PSUs and defence
establishments — almost exclusively.

**A real (non-fuzzy) join key exists**, though: `tenders_vps.tenders.
detail_url`'s final `A13h1`-delimited segment, base64-decoded, is exactly
`aoc_tenders.tender_id` (verified: `MjAxN19NRVNfMTUzNDY1XzE=` decodes to
`2017_MES_153465_1`, matching the `tender_id` format exactly).
`tenders_vps.tenders.tender_id` itself is a different, unrelated internal
scraper ID — not usable directly.

Using this real key against **E-IN-C Branch, Military Engineer Services**
(largest central org in both tables) still only matched 0-29% depending on
year — because the notice-side crawl for MES is concentrated in
2015-2018 and 2026, with almost nothing in between (checked directly: 1-3
rows/year for 2019-2025). This is a scrape-coverage gap specific to that
organisation/crawl window, not a formatting problem.

**Central Coalfields Limited**, tested the same way, matched >98% for
2019-2025 specifically (98.5-100% per year) after the 2013-2018 tail
(where its own coverage is thin) was excluded. This suggested the
join quality is real but organisation- and year-window-dependent, so the
other five Coal India Limited subsidiaries were tested the same way:

| Organisation | Matched | Total | Rate |
|---|---|---|---|
| Central Coalfields | 50,819 | 50,977 | 99.7% |
| Eastern Coalfields | 24,585 | 24,811 | 99.1% |
| Western Coalfields | 13,382 | 13,838 | 96.7% |
| South Eastern Coalfields | 21,468 | 21,847 | 98.3% |
| Northern Coalfields | 14,834 | 14,924 | 99.4% |
| Mahanadi Coalfields | 13,617 | 13,954 | 97.6% |
| **Total** | **138,705** | **140,351** | **98.8%** |

### Final slice: Coal India Limited subsidiaries, 2019-2025

Central Coalfields, Eastern Coalfields, Western Coalfields, South Eastern
Coalfields, Northern Coalfields, and Mahanadi Coalfields Limited — six
wholly-owned subsidiaries of Coal India Limited under the Ministry of
Coal. **140,351 award rows**, inside the 100k-300k target, with **98.8%
of rows joinable to real notice-side data** (bid dates, EMD) via the
base64-decoded `tender_id` key. This isn't literally "one state or 2-3
ministries" per Section 6's wording, but it's the same shape the plan
asks for — a single coherent, bounded organisational family, chosen on
verified coverage rather than preference.

This means F2, F9, and F11 are computable for ~98.8% of the slice, not
just the award-only flags (F1, F5, F12), which are unaffected by any of
this (they only ever needed award-side data).

**ETL implication:** the join key for loading `tender` rows from
`tenders_vps` is `base64_decode(detail_url.split('A13h1')[-1])`, matched
against `aoc_tenders.tender_id` — not any column literally named
"tender_id" on the notice side, and not free-text reference number
matching.

## Still open

- Postgres schema applied (Phase 1, confirmed). ETL to load this
  slice into Postgres is Phase 2 work, not yet done as of this revision.
