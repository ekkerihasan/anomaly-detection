# Data caveats

These are stated intentionally on-screen (UI empty states, deck, video),
per MHASH26-BUILD-PLAN.md Section 6 and CLAUDE.md rule 10. Naming a limit
is a scoring move, not a confession — never silently work around these.

The CPPP mirror does **not** include:

- **Estimated / pre-bid value** — "award value vs. estimate" flags are not
  computable from this data.
- **Per-bidder prices or losing bidders' names** — classic price-based
  cartel screens (bid variance, cover pricing) cannot be built.
- **PAN, GSTIN, or CIN** — vendor identity is free text only
  (`vendor.name_norm`, normalised exact match, never fuzzy/entity
  resolution). Language everywhere is "possible relationship, for review",
  never "same entity."
- **Conflict-of-interest or beneficial-ownership data.**

## Fields we do get

**Award side:** Tender Type, Tender Ref No, Organisation Name, Tender
Description, Published Date, Contract Date, Contract Value, Number of bids
received, Name of selected bidder, Address of selected bidder, Date of
Completion, Tender Document URL.

**Notice side:** Tender Reference Number, Tender Title, Organisation Name,
Organisation Type, Tender Category, Tender Type, Product Category,
ePublished Date, Bid Submission Start and End Date, Bid Opening Date, EMD,
Tender Fee, Location, Work Description.

## The H+4 gate

`Number of bids received` is the field F1_SINGLE_BID depends on. If it is
sparsely populated in the loaded slice, the whole plan pivots to
notice-side-only flags (F2, F9, F11, F12) — this must be known before ETL
design proceeds. See `scripts/inspect_schema.py` and the null-profiling
step in the ETL report.
