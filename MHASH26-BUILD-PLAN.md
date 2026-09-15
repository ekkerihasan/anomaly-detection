# M\#26 Round 1 Build Plan

## Automated Public Procurement Anomaly Detection

**Status:** active **Deadline:** Round 1 submission closes 17 September 2026 **Domain:** Smart Governance and Compliance **SDG:** 16, Peace, Justice and Strong Institutions

&nbsp;

---

## 0\. How to use this document

**Teammates:** read sections 1 to 4, then your own role block in section 11\. The rest is reference.

&nbsp;

**AI coding agents:** this is your context file. Attach it at the start of every session. Section 13 contains rules you must follow. Do not invent scope beyond section 5\. If a decision is not in this document, ask rather than assume.

&nbsp;

**Timing note:** the earlier research doc assumed a 72-hour window. Counting from now to end of day 17 September, the real window is closer to 48 hours. This plan is written in H+ hours from the moment work starts (H0). Every block has a hard definition of done. If a block overruns, cut scope inside it rather than pushing the next block.

&nbsp;

---

## 1\. Why this problem statement

We are locked into the Domain and SDG pair for Round 2\. Round 2 gives us a *different* problem statement carrying the same Smart Governance \+ SDG 16 tag. The other Governance statement is Post-Award Subcontractor Variations, so Round 2 is very likely the same shape: compare records across a process stage, surface what deserves human review.

&nbsp;

That means everything we build now is reusable. This is the main reason we chose this over higher-scoring options.

&nbsp;

Secondary reasons:

&nbsp;

- Real public data exists and is queryable immediately  
- The buyer has publicly asked for this capability  
- Ground truth exists, so we can validate instead of assert  
- Governance will be far less crowded than Healthcare or Cybersecurity, and only 30 teams advance

&nbsp;

---

## 2\. Evaluation criteria we are optimising for

**Round 1 (this submission):**

&nbsp;

1. Innovation and creativity beyond the stated requirements  
2. Feasibility and practicality of the solution  
3. Marketing and media strategy  
4. Monetisation strategy  
5. Adherence to the official template and submission guidelines  
6. Bonus marks for a working prototype

&nbsp;

Two of six are business criteria. This is where engineering teams lose. Section 9 and 10 are not optional.

&nbsp;

**Round 2 (36 hours onsite, if we advance):** technical implementation, innovation, user experience, scalability.

&nbsp;

**What this means for scope.** Round 1 rewards a credible, explainable, well-pitched thing. It does not reward a large thing. Build a thin real spine and spend the remaining effort on the frontend, the deck and the video.

&nbsp;

---

## 3\. The one-sentence product

> This does not detect corruption. It ranks tenders by how much they deviate from normal procurement behaviour, and shows the auditor exactly why, so that scarce human review time lands on the 200 tenders most worth reading instead of a random 200\.

&nbsp;

This sentence goes on a slide verbatim and is said out loud in the video. Every design decision should be checkable against it.

&nbsp;

---

## 4\. The three facts the pitch rests on

**Fact 1: the data is public and already parsed.** A public mirrored dump of the Central Public Procurement Portal exists as flat SQLite: roughly 4.9M award-of-contract records and 3.9M tender notices with parsed detail pages. It carries number of bids received, selected bidder name and address, contract value and contract date.

&nbsp;

**Fact 2: the buyer asked for this by name.** In May 2026 the CAG said India should use data and technology to detect unfair practices in tenders, that it is deploying AI/ML to move beyond sampling, and that its aim is near-real-time identification of procurement concentration and cartel risk indicators.

&nbsp;

**Fact 3: ground truth exists.** On 7 April 2026 the CCI found 17 electrical contractors guilty of bid rigging, cover bidding and rotation in Assam Police Housing Corporation tenders for electrification of 73 police stations. Excess cost to the state about ₹7.56 crore. Tenders were awarded in April 2018 and the case concluded in 2026\. Eight years.

&nbsp;

**VERIFY BEFORE THE DECK GOES IN.** All three of these are 2026 sources. One person must open each link in section 15 and confirm the exact figure and date before any of it appears on a slide. A wrong public-record claim in a submission about procurement integrity is an unusually expensive error.

&nbsp;

---

## 5\. Scope: what we build and what we do not

### In scope

| Component | Why |
| :---- | :---- |
| Slice ingest, SQLite to Postgres | Foundation, and reused in Round 2 |
| Currency and date parsers with tests | Silent parse failures kill three flags |
| Six deterministic SQL flags | Real detection, no entity resolution needed |
| Weighted score from a YAML config | Configurable, demoable, auditable |
| Ranked list and detail page | The product |
| Explanation card with real numbers | Scores on innovation in R1 and UX in R2 |
| Triage states (open / reviewing / referred / dismissed) | Converts "a dashboard" into "an audit tool" |
| Simplified back-test on the Assam case | The single most persuasive fifteen seconds |

### Out of scope, moved to the roadmap slide

Entity resolution and fuzzy vendor matching. The vendor graph, Louvain, award rotation detection. Peer-group percentile machinery. Benford. Live CPPP pulls. GeM and state portals. LLMs anywhere. Neo4j. Kafka. Auth beyond a hardcoded reviewer. Mobile.

&nbsp;

Cutting entity resolution is the key decision. It is the most expensive single piece, it gates the flags we dropped, and nothing in the six flags we kept needs it.

&nbsp;

**Roadmap framing:** these are not things we failed to build. They are the next release, and the deck says so with a diagram. That reads as scalability and feasibility to a judge.

&nbsp;

---

## 6\. Data

### Source

Primary corpus is the public CPPP mirror as SQLite. Cite `eprocure.gov.in` as the origin in the deck and README, not the mirror. Verify SHA-256 before use. Keep our own minimal scraper in the repo so the pipeline is not *dependent* on a third-party host, and make sure it actually works against at least one organisation before anyone claims it does.

&nbsp;

If a judge asks whether this is legal: it is Government of India data published for public view under the CPPP transparency mandate, and we re-derive it ourselves.

### Fields we get

From the award side: Tender Type, Tender Ref No, Organisation Name, Tender Description, Published Date, Contract Date, Contract Value, Number of bids received, Name of selected bidder, Address of selected bidder, Date of Completion, Tender Document URL.

&nbsp;

From the notice side: Tender Reference Number, Tender Title, Organisation Name, Organisation Type, Tender Category, Tender Type, Product Category, ePublished Date, Bid Submission Start and End Date, Bid Opening Date, EMD, Tender Fee, Location, Work Description.

### Fields we do NOT get

State these on a slide. Naming limits is a scoring move, not a confession.

&nbsp;

- No estimated or pre-bid value, so "award value vs estimate" flags are impossible  
- No per-bidder prices and no losing bidders' names, so classic price-based cartel screens are not computable from this data  
- No PAN, GSTIN or CIN, so vendor identity is free text  
- No conflict-of-interest or beneficial ownership data

### The slice

Do not load everything. Pick **one state or two or three ministries with good coverage**, five financial years, targeting 100k to 300k award rows. Coverage decides this at H+4, not preference.

&nbsp;

Reason: every query stays under a second on camera, and the ETL finishes inside one block.

&nbsp;

---

## 7\. Schema

CREATE TABLE organisation (

&nbsp;

&nbsp;&nbsp;id          BIGSERIAL PRIMARY KEY,

&nbsp;

&nbsp;&nbsp;name        TEXT NOT NULL,

&nbsp;

&nbsp;&nbsp;name\_norm   TEXT NOT NULL,

&nbsp;

&nbsp;&nbsp;org\_type    TEXT,

&nbsp;

&nbsp;&nbsp;state       TEXT

&nbsp;

);

&nbsp;

CREATE TABLE vendor (

&nbsp;

&nbsp;&nbsp;id          BIGSERIAL PRIMARY KEY,

&nbsp;

&nbsp;&nbsp;name\_raw    TEXT NOT NULL,

&nbsp;

&nbsp;&nbsp;name\_norm   TEXT NOT NULL,

&nbsp;

&nbsp;&nbsp;address\_raw TEXT,

&nbsp;

&nbsp;&nbsp;address\_norm TEXT

&nbsp;

);

&nbsp;

CREATE TABLE tender (

&nbsp;

&nbsp;&nbsp;id                BIGSERIAL PRIMARY KEY,

&nbsp;

&nbsp;&nbsp;ref\_no            TEXT,

&nbsp;

&nbsp;&nbsp;org\_id            BIGINT REFERENCES organisation(id),

&nbsp;

&nbsp;&nbsp;title             TEXT,

&nbsp;

&nbsp;&nbsp;description       TEXT,

&nbsp;

&nbsp;&nbsp;category          TEXT,

&nbsp;

&nbsp;&nbsp;product\_category  TEXT,

&nbsp;

&nbsp;&nbsp;tender\_type       TEXT,

&nbsp;

&nbsp;&nbsp;epublished\_date   DATE,

&nbsp;

&nbsp;&nbsp;bid\_start\_date    DATE,

&nbsp;

&nbsp;&nbsp;bid\_end\_date      DATE,

&nbsp;

&nbsp;&nbsp;bid\_open\_date     DATE,

&nbsp;

&nbsp;&nbsp;emd               NUMERIC,

&nbsp;

&nbsp;&nbsp;tender\_fee        NUMERIC,

&nbsp;

&nbsp;&nbsp;detail\_url        TEXT

&nbsp;

);

&nbsp;

CREATE TABLE award (

&nbsp;

&nbsp;&nbsp;id              BIGSERIAL PRIMARY KEY,

&nbsp;

&nbsp;&nbsp;tender\_id       BIGINT REFERENCES tender(id),

&nbsp;

&nbsp;&nbsp;vendor\_id       BIGINT REFERENCES vendor(id),

&nbsp;

&nbsp;&nbsp;contract\_value  NUMERIC,

&nbsp;

&nbsp;&nbsp;contract\_date   DATE,

&nbsp;

&nbsp;&nbsp;bids\_received   INT,

&nbsp;

&nbsp;&nbsp;completion\_days INT,

&nbsp;

&nbsp;&nbsp;detail\_url      TEXT

&nbsp;

);

&nbsp;

CREATE TABLE flag (

&nbsp;

&nbsp;&nbsp;id         BIGSERIAL PRIMARY KEY,

&nbsp;

&nbsp;&nbsp;award\_id   BIGINT REFERENCES award(id),

&nbsp;

&nbsp;&nbsp;code       TEXT NOT NULL,        \-- 'F1\_SINGLE\_BID'

&nbsp;

&nbsp;&nbsp;severity   NUMERIC NOT NULL,     \-- 0..1

&nbsp;

&nbsp;&nbsp;evidence   JSONB NOT NULL,       \-- the numbers behind the sentence

&nbsp;

&nbsp;&nbsp;created\_at TIMESTAMP DEFAULT now()

&nbsp;

);

&nbsp;

CREATE TABLE risk\_score (

&nbsp;

&nbsp;&nbsp;award\_id    BIGINT PRIMARY KEY REFERENCES award(id),

&nbsp;

&nbsp;&nbsp;score       NUMERIC NOT NULL,

&nbsp;

&nbsp;&nbsp;rank        INT,

&nbsp;

&nbsp;&nbsp;computed\_at TIMESTAMP DEFAULT now()

&nbsp;

);

&nbsp;

CREATE TABLE review (

&nbsp;

&nbsp;&nbsp;award\_id   BIGINT PRIMARY KEY REFERENCES award(id),

&nbsp;

&nbsp;&nbsp;status     TEXT NOT NULL DEFAULT 'open',  \-- open|reviewing|referred|dismissed

&nbsp;

&nbsp;&nbsp;note       TEXT,

&nbsp;

&nbsp;&nbsp;updated\_at TIMESTAMP DEFAULT now()

&nbsp;

);

&nbsp;

\-- Round 2 lands here. Create the table now, leave it empty.

&nbsp;

CREATE TABLE contract\_variation (

&nbsp;

&nbsp;&nbsp;id            BIGSERIAL PRIMARY KEY,

&nbsp;

&nbsp;&nbsp;award\_id      BIGINT REFERENCES award(id),

&nbsp;

&nbsp;&nbsp;variation\_no  INT,

&nbsp;

&nbsp;&nbsp;varied\_on     DATE,

&nbsp;

&nbsp;&nbsp;value\_delta   NUMERIC,

&nbsp;

&nbsp;&nbsp;reason        TEXT,

&nbsp;

&nbsp;&nbsp;subcontractor TEXT

&nbsp;

);

&nbsp;

`flag.evidence` is the load-bearing column. Every flag writes the numbers that produced it, and the UI renders from that. This is what makes the explanation panel trivial to build.

&nbsp;

`vendor.name_norm` exists but we are **not** clustering on it in Round 1\. Normalise only. Exact-match on `name_norm` is enough for the back-test.

&nbsp;

---

## 8\. The six flags

All six are SQL over `award` joined to `tender`. None need entity resolution. Each writes an `evidence` JSON blob and a `severity` between 0 and 1\.

### F1\_SINGLE\_BID

Only one bid received on a competitively advertised tender. Basis: OCP red flag 1, GFR competition principle. `WHERE a.bids_received = 1 AND t.tender_type ILIKE '%open%'` Evidence: `{bids_received, tender_type, peer_median_bids}` Severity: 1.0 if value above ₹50L, else 0.7

### F2\_SHORT\_WINDOW

Bid submission window shorter than the statutory minimum. Basis: GFR 2017 Rule 161, three weeks for advertised tender enquiry, four weeks where bids are invited from abroad. `WHERE (t.bid_end_date - t.epublished_date) < 21` Evidence: `{window_days, required_days: 21, epublished_date, bid_end_date}` Severity: scale linearly, 20 days is 0.3, 7 days or fewer is 1.0

### F5\_THRESHOLD\_BUNCHING

Contract value sitting just below a procedural threshold. Basis: GFR Rule 162 (limited tender enquiry up to ₹50 lakh), Rule 155 (purchase committee ₹50,000 to ₹5 lakh), Rule 154 (without quotation up to ₹50,000). Splitting demand to stay under an approval threshold is a standing CAG finding. Flag when value falls within 5% below ₹50,00,000, ₹5,00,000 or ₹50,000. Evidence: `{contract_value, threshold, gap_pct, rule}` Severity: 1.0 within 1%, 0.6 within 5%

### F9\_INSTANT\_AWARD

Award made with near-zero evaluation time after bid opening. Basis: OCP, decision period extremely short. `WHERE (a.contract_date - t.bid_open_date) <= 1` Evidence: `{decision_days, bid_open_date, contract_date, peer_median_days}` Severity: 1.0 at 0 days, 0.6 at 1 day

### F11\_EMD\_ANOMALY

Earnest money deposit disproportionate to contract value. Very high EMD is gatekeeping, zero EMD is low deterrence. Basis: GFR EMD norms. Compute `emd / contract_value`. Flag the top and bottom 2% within the organisation. Evidence: `{emd, contract_value, ratio, peer_ratio_median}` Severity: 0.5 to 0.9 by distance from median

### F12\_YEAR\_END\_RUSH

Awards clustered in the last two weeks of March. Basis: standard audit practice. `WHERE EXTRACT(MONTH FROM a.contract_date) = 3 AND EXTRACT(DAY FROM a.contract_date) >= 18` Evidence: `{contract_date, org_march_share, org_annual_share}` Severity: 0.4 alone, but it compounds

### Scoring

score \= Σ (weight\[code\] × severity) for all flags on that award

&nbsp;

Weights live in `config/weights.yaml`, **not in code**. Show the file on camera. The line to say: "our thresholds are configurable by the audit body, because ₹50 lakh in a municipal body is not ₹50 lakh in NHAI."

&nbsp;

Rank within the loaded slice. Do not claim a national percentile we have not computed.

### False positives

When a judge asks, the answer is: raw single indicators produce mass false positives, which is why OCP's own guidance says indicators must be triangulated and locally calibrated. We score on combinations, we rank rather than accuse, and we report precision-at-K rather than accuracy because there is no labelled negative set and never will be.

&nbsp;

---

## 9\. The back-test

This is the deliverable that wins the round. Protect the time for it.

&nbsp;

**Method.** Pull every award in our slice from Assam Police Housing Corporation Limited and Assam electrification works, roughly 2017 to 2018\. Score them. Check where the tenders named in the CCI's 7 April 2026 order rank.

&nbsp;

**Outcomes, all usable:**

&nbsp;

- Top percentile: headline is "the engine flags in N seconds what took an audit office and the CCI eight years." Put the exact number on the slide.  
- Middling: headline is "recall at 5% review budget: N of M." Still strong, still honest.  
- Not in the corpus: **do not fake it.** Fall back to a synthetic injection test. Take a clean organisation's real award history, programmatically inject a splitting pattern and a rotation pattern, report precision-at-K, and say explicitly on screen that it is synthetic. A team that reports a synthetic benchmark honestly outscores one reporting a real-sounding number it cannot defend.

&nbsp;

**Decide by H+10.** If the Assam data is not there, we need the remaining time to build the fallback.

&nbsp;

---

## 10\. Frontend spec

Three screens. Next.js App Router, React, server-side scoring only. No business logic in the frontend.

### Screen 1: ranked list

- Table of awards sorted by score descending  
- Columns: rank, organisation, vendor, value, date, score, flag chips  
- Filters: organisation, value band, date range, flag code, review status  
- Row click goes to detail

### Screen 2: detail / explanation card

This is the highest-value component in the build. Design it at H0 against fake JSON, before there is real data.

&nbsp;

- Header: award identity, contract value, date, link to the original CPPP page  
- Score with its rank in the slice  
- **One row per flag**, each showing: a plain-English sentence, the actual numbers from `evidence`, and the rule or basis it comes from  
  - Example: "Only one bid was received. Comparable tenders in this category averaged 4.2 bids." plus "GFR competition principle, OCP red flag 1"  
  - Example: "The bid window was 9 days. GFR Rule 161 requires 21 days for an advertised tender enquiry."  
- Triage control: open / reviewing / referred / dismissed, plus a reviewer note

### Screen 3: organisation summary

- Single-bid rate, award concentration by exact vendor name, value distribution, March clustering  
- Enough to make the point that the tool works at aggregate level too

### Non-negotiables

- Numbers must be legible at video resolution. Judges watch small.  
- Empty states and loading states exist.  
- No vendor names visible in any screenshot used in the deck or video unless the case is a published CCI order. See section 12\.

&nbsp;

---

## 11\. Schedule and roles

Roles: **D** data and pipeline, **E** engine (flags and scoring), **F** frontend, **P** pitch (deck, business, video), **L** lead (integrates, owns the demo, floats).

### H0 to H6: prove the data, then commit

- **D:** download the dump, verify SHA-256, open it, count rows, profile nulls on the six fields we need. **Report at H+4: is `Number of bids received` populated, and at what rate?** If it is mostly empty, the whole plan pivots to notice-side flags (F2, F9, F11, F12) and we need to know now, not at H+30.  
- **L:** run the Assam query. Do those tenders exist in our corpus? Decide back-test versus synthetic fallback by H+10.  
- **E:** repo up, Postgres running, schema applied.  
- **F:** Next.js scaffolded, detail card built against hardcoded fake JSON.  
- **P:** read the official M\#26 template end to end, build the skeleton deck with every required slide as an empty heading. **Start with the monetisation slide.** It is the one that gets rushed otherwise.

&nbsp;

**Done when:** we know the data is usable and the back-test path is decided.

### H6 to H18: ingest and first flags

- **D:** SQLite to Postgres ETL. Parse JSON detail blobs into columns. Currency and date parsers with unit tests against 50 real strings pulled from the dump. Log every value the parser rejects. A silent `None` here quietly kills three flags.  
- **E:** F1, F2, F5, F9, F11, F12 as SQL. Write `evidence` JSON for each.  
- **F:** real card component, list view, filters wired to the API.  
- **P:** slides 1 to 4 (problem, evidence, what it does, how it works). The CAG quote and the Assam numbers are the spine.

&nbsp;

**Done when:** flags run over the loaded slice and produce rows in `flag`.

### H18 to H30: scoring, back-test, polish

- **E:** weights YAML, composite score, ranking. Recompute over the whole slice.  
- **L \+ D:** **run the back-test.** Produce the single number that goes on the results slide. This is the deliverable of this block. Protect it.  
- **F:** detail page explanation panel rendering from `evidence`, triage state control, organisation summary screen.  
- **P:** monetisation and marketing slides **finished, not drafted.** L reviews them.

&nbsp;

**Done when:** the number exists and the explanation panel renders real evidence.

### H30 to H40: freeze, deploy, rehearse

- **Feature freeze at H+30.** Non-negotiable. Everything after is polish, deploy and video.  
- **L:** deploy to one box (Docker Compose, or Render/Railway). The demo must not depend on a laptop. Seed a known-good demo state: the exact filters and the exact award that opens on camera. Never demo a query you have not run twice.  
- **F:** empty states, loading states, legibility pass at video resolution.  
- **P:** script the video to the second.

&nbsp;

**Done when:** the demo runs end to end from a URL, twice, without intervention.

### H40 to H48: video and submission

- Record. All five members on camera, per the rules. Screen capture separately from talking heads and cut together. Do not try to do both live.  
- Two minutes without a prototype, three with one. Build for three, then check that the first two minutes stand alone if the edit runs long.  
- Submit with hours to spare. Deadlines get extended; uploads do not get faster.

&nbsp;

---

## 12\. The business half

### Market framing

Use CPPP's own published figures, not a consultancy TAM estimate. They are verifiable and they are the government's own numbers. Re-verify the current month's figures from the newsletter page before the deck goes in and state the period plainly.

&nbsp;

The argument is not "the market is ₹X crore". It is:

&nbsp;

> Every one of these awards is reviewed by sampling, after the fact, by people. There is no systematic screen. The cost of a miss is measurable: one Assam scheme, ₹7.56 crore, eight years to conclude.

### Monetisation: a ladder, not one buyer

1. **Free public tier.** Anyone can search a vendor or an organisation and see its risk profile. Costs us nothing, drives all the media, anchors credibility. This is the marketing strategy and the product at once.  
2. **Audit firms and internal audit.** Big four and mid-tier firms doing statutory and internal audit of PSUs and state undertakings. They bill by the hour and buy tools that cut review hours. Fastest revenue, shortest sales cycle, no government procurement at all. **This is the primary named buyer on the slide.**  
3. **PSU and large-buyer internal vigilance.** Sold as self-defence: find it before CAG does.  
4. **Multilateral-funded projects.** World Bank, ADB, AIIB-funded state projects carry fiduciary and procurement-compliance obligations. There is a budget line here and the funder can mandate it.  
5. **Bidder side.** A contractor who lost a tender to a pattern will pay to see the pattern. Frame carefully as "market intelligence and bid-fairness reporting", keep it secondary.

&nbsp;

Pricing shape: per-seat SaaS for the audit tier, priced against the hourly cost it displaces. Per-portal or per-state subscription for institutional. Paid API for RegTech vendors. **State a specific pilot price.** A defensible number beats a business-model diagram.

&nbsp;

**Government as buyer is the roadmap slide, not the revenue slide.**

### Marketing and media

- **Publish an index.** A quarterly "single-bid rate by state and ministry" leaderboard from public data. Journalists cannot resist a ranking, and it gives us a recurring news cycle we control.  
- **Give it to data-journalism desks first.** Indian Express, The Hindu, Scroll, IndiaSpend, Factly run exactly this story. One story with our name on it beats any ad spend.  
- **Open-source the flag library, keep the platform commercial.** Same play as OCP's Cardinal. Contributors become our calibration.  
- **Map output to OCDS** so international bodies and funders can consume it. One line on the slide, high credibility per word.

&nbsp;

---

## 13\. Rules for AI coding agents

1. Scope is section 5\. Do not build anything in the "out of scope" list, however easy it looks.  
2. No LLM in the scoring path. If an LLM appears at all it is one disclosed use, turning a computed flag into a plain-English sentence, and it never influences the score. "We did not use an LLM to decide" is a trust feature in an audit product.  
3. Every flag writes `evidence` JSON. A flag with no evidence blob is not done.  
4. Weights and thresholds live in `config/weights.yaml`. Never hardcode a threshold in a query or a component.  
5. All scoring is server-side. The frontend renders, it does not compute.  
6. Currency parsing gets unit tests before anything depends on it. Values arrive as `"1,23,45,678.00"`, `"Rs. 45,00,000"`, `"NA"`, `""`, sometimes in lakhs. One parser, tested, with a reject log.  
7. Never claim vendor identity. We match on normalised exact names only. The language is "possible relationship, for review", never "same entity".  
8. No new dependencies without asking. Stack is fixed: Python, Postgres, FastAPI, Next.js, pandas or DuckDB for exploration. No Neo4j, no Kafka, no ORM migration framework, no auth library.  
9. Prefer a working narrow thing over a general framework. This is a 48-hour build, not a platform.  
10. If the data does not support a feature, say so and stop. Do not synthesise values to make a screen look full.

&nbsp;

---

## 14\. Risks

| Risk | Likelihood | Mitigation |
| :---- | :---- | :---- |
| `Number of bids received` sparsely populated | Medium | H+4 profiling gate; pivot to notice-side flags |
| Assam tenders absent from corpus | Medium | Decide by H+10; synthetic injection fallback |
| Mirror host down mid-build | Low | Download to local plus a shared drive at H0 |
| Value parsing silently drops records | High | Reject log and a count of unparsed values; report the coverage figure in the deck |
| Scope creep into entity resolution or the graph | High | Section 5 is the contract. Say no now. |
| Deck rushed into the last six hours | High | P owns slides from H0; freeze at H+30 |
| Named vendors shown in a public video | Medium | **Anonymise or redact vendor names in the deck and video** unless the case is a published CCI order. A real firm's name next to the word "risk" in a public submission is a defamation exposure we do not need. Use real names in the live tool, redact in the artefacts. |

&nbsp;

That last row is not a formality. It is also the kind of judgement a judge notices.

&nbsp;

---

## 15\. Submission checklist

- [ ] Official M\#26 template, exported as **PDF**  
- [ ] Filename exactly `TeamID_TeamName_ProblemStatementID`  
- [ ] **No institute name, logo or identifiable background** anywhere in the deck or video. Check the video frame by frame: a lanyard, a hostel door, a whiteboard.  
- [ ] All five members on camera  
- [ ] Video under 3 minutes (prototype) or 2 minutes (no prototype)  
- [ ] First two minutes stand alone if the edit runs long  
- [ ] GitHub repo **public**. Open the repo link and the video link in an **incognito window on mobile data**, not campus wifi.  
- [ ] Vendor names redacted in all artefacts  
- [ ] All three 2026 claims (CAG, CCI, CPPP figures) verified against source  
- [ ] Submitted with hours to spare

&nbsp;

---

## 16\. Demo script, three minutes

1. **0:00-0:20** The Assam case in one sentence: 17 contractors, bid rotation, ₹7.56 crore, found by hand, concluded eight years later.  
2. **0:20-0:35** CAG in May 2026 asking for exactly this capability. One line on screen.  
3. **0:35-1:10** The tool. Real CPPP data, N awards loaded, ranked list. Click the top one. The explanation panel reads out: single bid, 9-day window against a 21-day rule, year-end award.  
4. **1:10-1:40** Organisation view. Single-bid rate against peers, concentration, March clustering.  
5. **1:40-2:10** **The back-test number. Where the known-cartel tenders rank.**  
6. **2:10-2:35** Triage: mark as referred, add a note. "This is an auditor's queue, not a verdict."  
7. **2:35-3:00** Who pays, and the Round 2 line: same engine, post-award variations.

&nbsp;

Step 5 is the most persuasive fifteen seconds. Everything else is table stakes in a hackathon; a measured result against a real conviction is not.

&nbsp;

---

## 17\. Open questions, assign owners now

1. Which slice? Coverage decides at H+4, not preference.  
2. Do we open-source the flag library at Round 1 or hold it to Round 2? Recommendation: open at Round 1\. The edge loss is negligible at hackathon timescales and it makes the marketing slide concrete.  
3. Does anyone have a journalist or audit-firm contact who will give us fifteen minutes? A single quote from a practising auditor on "how many tenders can you actually review" is worth a slide.  
4. Who records and edits the video? Assign at H0, not H+40.

&nbsp;

---

## 18\. Sources

- CPPP mirror, schema and record counts: [https://tender.sarthaksidhant.com/](https://tender.sarthaksidhant.com/)  
- CPPP bid awards and portal FAQ: [https://eprocure.gov.in/](https://eprocure.gov.in/)  
- OCP, *Red Flags in Public Procurement* (2024), 73 indicators mapped to OCDS: [https://www.open-contracting.org/resources/red-flags-in-public-procurement-a-guide-to-using-data-to-detect-and-mitigate-risks/](https://www.open-contracting.org/resources/red-flags-in-public-procurement-a-guide-to-using-data-to-detect-and-mitigate-risks/)  
- OCP Cardinal, open-source red-flags library: [https://github.com/open-contracting/cardinal-rs](https://github.com/open-contracting/cardinal-rs)  
- CAG on AI/ML and cartel risk indicators, May 2026: [https://aninews.in/news/business/cag-calls-for-use-of-data-tech-to-detect-unfair-practices-in-govt-tenders20260520121607/](https://aninews.in/news/business/cag-calls-for-use-of-data-tech-to-detect-unfair-practices-in-govt-tenders20260520121607/)  
- CCI order, 17 contractors, APHCL electrification, 7 April 2026: [https://cms-induslaw.com/en/ind/publication/the-sentinel-the-quarterly-news-bulletin-in-competition-law-april-june-2026](https://cms-induslaw.com/en/ind/publication/the-sentinel-the-quarterly-news-bulletin-in-competition-law-april-june-2026)  
- CCI, HP India and 21 resellers, GeM tender manipulation, July 2026: [https://english.dainikjagranmpcg.com/national/cci-cracks-down-on-hp-india-cartel-21-resellers-named/article-22991](https://english.dainikjagranmpcg.com/national/cci-cracks-down-on-hp-india-cartel-21-resellers-named/article-22991)  
- CAG audit of Delhi e-procurement, shared PANs, emails, IPs across competing bids: [https://www.policyedge.in/p/cag-audit-flags-systemic-gaps-in-delhis-gst-oversight-power-subsidy-and-e-procurement](https://www.policyedge.in/p/cag-audit-flags-systemic-gaps-in-delhis-gst-oversight-power-subsidy-and-e-procurement)  
- GFR 2017 Rule 161, bid submission period: [https://www.gfr.co.in/p/gfr-advertised-tender-enquiry.html](https://www.gfr.co.in/p/gfr-advertised-tender-enquiry.html)  
- GFR 2017 Rule 162, limited tender enquiry, ₹50 lakh: [https://constitutionofindia.in/rule-162-of-the-general-financial-rules-2017-limited-tender-enquiry/](https://constitutionofindia.in/rule-162-of-the-general-financial-rules-2017-limited-tender-enquiry/)  
- M\#26 hackathon portal: [https://hackathon.manipal.edu/](https://hackathon.manipal.edu/)

&nbsp;