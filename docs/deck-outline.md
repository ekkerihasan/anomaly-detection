# Deck skeleton (headings only)

**Not the final deck.** This is a placeholder structure built from the
content already specified in MHASH26-BUILD-PLAN.md, so slide-writing can
start before real data/back-test numbers exist. Section 0 of the build
plan says the *official* M#26 template must be read end to end and the
submission must follow it exactly (filename, required slides, PDF export)
— nobody on this build has fetched that template yet. Reconcile this
outline against the official template before treating any slide as final.

Per Section 11, **start with the monetisation slide** — it's the one that
gets rushed otherwise.

1. **Monetisation** — the ladder (Section 12): free public tier -> audit
   firms (primary named buyer) -> PSU/vigilance -> multilateral-funded
   projects -> bidder-side intelligence. Specific pilot price, stated.
2. **Title / one-sentence product** (Section 3, verbatim on slide).
3. **Problem** — Assam case in one sentence: 17 contractors, bid rotation,
   ~Rs 7.56 crore, found by hand, concluded eight years later. **Verify
   this figure and date against the source before it goes in** (Section 4
   flags all three headline facts as needing verification).
4. **Evidence / why now** — CAG, May 2026, calling for AI/ML procurement
   screening. One line, verified quote.
5. **What it does** — the one-sentence product again, plus the three
   screens.
6. **How it works** — six deterministic SQL flags, no entity resolution,
   no LLM in the scoring path. Show `config/weights.yaml` on camera.
7. **Data & its limits** — sourced from eprocure.gov.in, slice size and
   coverage, and the explicit caveats in `docs/data-caveats.md`.
8. **The back-test result** — the single most persuasive number (Section
   9). Real Assam back-test if the tenders are in the loaded slice;
   otherwise the explicitly-labeled synthetic injection test.
9. **Marketing strategy** — quarterly single-bid-rate leaderboard,
   data-journalism partners, open-sourced flag library, OCDS mapping.
10. **Roadmap** — entity resolution, vendor graph, award rotation
    detection, peer-group percentiles, Benford's law, live CPPP pulls,
    Round 2 (post-award subcontractor variations, same engine).
11. **Team.**
