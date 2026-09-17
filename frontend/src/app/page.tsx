import Link from "next/link";
import SyntheticBanner from "@/components/SyntheticBanner";
import { fetchDatasetMeta } from "@/lib/api";

/* Flag explanations for the bento grid — static audit knowledge base. */
const AUDIT_FLAGS = [
  {
    code: "F1",
    label: "SINGLE BID",
    title: "Single-Bidder Awards",
    desc: "Open tenders that attracted exactly one bidder. When competitive tenders receive only one response, genuine market price discovery is absent.",
    rule: "GFR 2017 Rule 161",
    metric: "1 Bidder Received",
    tag: "High Priority",
  },
  {
    code: "F2",
    label: "SHORT WINDOW",
    title: "Compressed Bid Windows",
    desc: "Tenders published with submission windows below statutory minimums (under 21 days), effectively restricting participation to pre-informed vendors.",
    rule: "GFR 2017 Rule 161",
    metric: "< 21 Days Window",
    tag: "Access Barrier",
  },
  {
    code: "F5",
    label: "THRESHOLD BUNCH",
    title: "Threshold Bunching",
    desc: "Contract values clustered suspiciously right below mandatory tender or higher-authority approval thresholds to bypass scrutiny.",
    rule: "GFR 2017 Rules 154 / 155 / 162",
    metric: "Clustered Just Below Limit",
    tag: "Oversight Evasion",
  },
  {
    code: "F9",
    label: "INSTANT AWARD",
    title: "Instant Award Decisions",
    desc: "Tenders evaluated and awarded abnormally fast after bid opening, indicating technical evaluations were predetermined or perfunctory.",
    rule: "CVC Guidelines & OCP RF-06",
    metric: "< 48h from Bid Close",
    tag: "Evaluation Risk",
  },
  {
    code: "F11",
    label: "EMD ANOMALY",
    title: "EMD Discrepancies",
    desc: "Earnest Money Deposit amounts that deviate sharply from statutory norms (2%–5% of contract value), suggesting selective bidder deterrents.",
    rule: "GFR 2017 Rule 170",
    metric: "Off-Scale Deposit",
    tag: "Bid Rigging Risk",
  },
  {
    code: "F12",
    label: "YEAR-END RUSH",
    title: "March Fiscal Rush",
    desc: "Spike in hasty tender approvals within the final two weeks of the fiscal year driven by budget lapse pressure, compromising due diligence.",
    rule: "CAG Audit Standards",
    metric: "Last 14 Days of FY",
    tag: "Lapse Avoidance",
  },
];

export default async function Home() {
  const meta = await fetchDatasetMeta();
  const awards = meta?.awards ?? 138512;
  const scored = meta?.scored ?? 131048;

  return (
    <>
      <SyntheticBanner />

      {/* ═══════════════════════════════════════════════════════════
          HERO SECTION
      ═══════════════════════════════════════════════════════════ */}
      <section className="relative neo-grid-bg overflow-hidden border-b-[2.5px] border-charcoal">
        <div className="max-w-7xl mx-auto w-full px-5 py-14 md:py-20 flex flex-col gap-10">
          
          {/* Header Badges */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="neo-badge neo-badge-dark">SDG 16 · ACCOUNTABLE INSTITUTIONS</span>
            <span className="neo-badge neo-badge-orange">PUBLIC PROCUREMENT AUDIT</span>
            <span className="neo-badge neo-badge-ghost">GFR 2017 COMPLIANT</span>
          </div>

          {/* Main Headline & Proposition */}
          <div className="max-w-4xl flex flex-col gap-5">
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-charcoal leading-[1.08]">
              DETECT PROCUREMENT{" "}
              <span className="relative inline-block text-orange underline decoration-charcoal decoration-[3px] underline-offset-8">
                ANOMALIES
              </span>{" "}
              BEFORE THEY SETTLE.
            </h1>

            <p className="text-lg md:text-xl text-charcoal-light max-w-3xl leading-relaxed">
              Not speculative AI scores — <strong>statutory deviation ranking</strong>. We evaluate
              every government tender award against 6 deterministic procurement audit rules so
              scarce auditor hours focus immediately on the contracts where statutory rules
              broke down.
            </p>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link href="/awards" className="neo-btn text-base px-6 py-3.5">
              <span>Open Review Queue</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12" />
                <polyline points="12 5 19 12 12 19" />
              </svg>
            </Link>

            <Link href="/awards/demo" className="neo-btn-dark text-base px-6 py-3.5">
              <span>Inspect Sample Anomaly</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </Link>
          </div>

          {/* Live Sample Preview Card */}
          <div className="neo-card p-5 md:p-6 bg-white mt-2 max-w-4xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b-[1.5px] border-concrete-border">
              <div className="flex items-center gap-3">
                <span className="neo-badge neo-badge-dark text-xs">SAMPLE FINDING</span>
                <span className="text-xs font-mono font-semibold text-concrete">ECL/MINING/2024/T-842</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-concrete uppercase">Composite Risk Score</span>
                <span className="neo-badge neo-badge-orange text-xs font-mono">2.14 / 3.00</span>
              </div>
            </div>

            <div className="grid sm:grid-cols-3 gap-4 pt-4 text-sm">
              <div className="flex flex-col gap-1">
                <span className="text-xs uppercase font-mono text-concrete font-bold">Organisation</span>
                <span className="font-semibold text-charcoal">Eastern Coalfields Limited</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-xs uppercase font-mono text-concrete font-bold">Contract Value</span>
                <span className="font-mono font-bold text-charcoal">₹ 4,18,50,000</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-xs uppercase font-mono text-concrete font-bold">Statutory Violations</span>
                <div className="flex flex-wrap gap-1.5">
                  <span className="neo-badge neo-badge-beige text-[0.65rem]">F1 · Single Bid</span>
                  <span className="neo-badge neo-badge-beige text-[0.65rem]">F2 · 4-Day Window</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════
          AUDIT METRICS TICKER
      ═══════════════════════════════════════════════════════════ */}
      <section className="bg-charcoal text-beige border-b-[2.5px] border-charcoal">
        <div className="max-w-7xl mx-auto w-full grid grid-cols-2 md:grid-cols-4 divide-x-[1.5px] divide-charcoal-light">
          {[
            {
              value: awards.toLocaleString("en-IN"),
              label: "Tenders Ingested",
              sub: "CPPP Mirror · Coal India Subsidiaries",
            },
            {
              value: "166,047",
              label: "Statutory Red Flags",
              sub: "Across 6 GFR 2017 Audit Rules",
            },
            {
              value: "6",
              label: "Deterministic Rules",
              sub: "Zero LLM Scoring · 100% Auditable",
            },
            {
              value: scored.toLocaleString("en-IN"),
              label: "Awards Scored & Ranked",
              sub: "Deviation Scores 0.16 – 2.45",
            },
          ].map((stat, i) => (
            <div key={i} className="flex flex-col gap-1.5 px-5 py-6 md:py-8">
              <span className="text-3xl md:text-4xl font-bold font-mono tracking-tight text-orange">
                {stat.value}
              </span>
              <span className="text-sm font-bold tracking-wide uppercase text-white">
                {stat.label}
              </span>
              <span className="text-xs text-concrete-light font-mono">
                {stat.sub}
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════
          HOW IT OPERATES — 3 STEPS
      ═══════════════════════════════════════════════════════════ */}
      <section className="neo-dot-bg border-b-[2.5px] border-charcoal py-16 md:py-20">
        <div className="max-w-7xl mx-auto w-full px-5 flex flex-col gap-10">
          
          <div className="flex flex-col gap-2">
            <span className="neo-badge neo-badge-dark w-fit">WORKFLOW</span>
            <h2 className="text-3xl md:text-4xl font-bold text-charcoal tracking-tight">
              From Public Tender to Prioritized Audit
            </h2>
            <p className="text-concrete text-base max-w-2xl">
              A transparent 3-stage audit pipeline converting messy procurement publications into
              an actionable, defensible investigation queue.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                step: "01",
                title: "Ingest & Normalize",
                desc: "Public CPPP mirror datasets (eprocure.gov.in) are cryptographically SHA-256 verified, cleaned of currency anomalies, and parsed into unified schema records.",
              },
              {
                step: "02",
                title: "Deterministic Rule Engine",
                desc: "Six statutory SQL rules evaluate each tender independently. Each finding captures exact quantitative evidence (bidders, dates, values) without black-box inference.",
              },
              {
                step: "03",
                title: "Rank-Ordered Triage",
                desc: "Auditors begin directly at rank #1. Every award presents the exact statutory rule citation and evidence values so findings stand up to legal review.",
              },
            ].map((item, i) => (
              <div
                key={i}
                className="neo-card p-6 flex flex-col gap-4 bg-white"
              >
                <div className="flex items-center justify-between">
                  <span className="text-3xl font-bold font-mono text-orange">
                    {item.step}
                  </span>
                  <span className="neo-badge neo-badge-beige text-xs">STAGE {item.step}</span>
                </div>
                <h3 className="text-xl font-bold text-charcoal">{item.title}</h3>
                <p className="text-sm text-charcoal-light leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════
          6 STATUTORY AUDIT RULES (BENTO GRID)
      ═══════════════════════════════════════════════════════════ */}
      <section className="bg-beige-alt border-b-[2.5px] border-charcoal py-16 md:py-20 neo-grid-bg">
        <div className="max-w-7xl mx-auto w-full px-5 flex flex-col gap-10">
          
          <div className="flex flex-col gap-2">
            <span className="neo-badge neo-badge-orange w-fit">STATUTORY RULESET</span>
            <h2 className="text-3xl md:text-4xl font-bold text-charcoal tracking-tight">
              6 Deterministic Audit Rules
            </h2>
            <p className="text-charcoal-light text-base max-w-2xl">
              Every flag represents a recognized procurement standard under General Financial Rules (GFR 2017)
              and Central Vigilance Commission guidelines. No probabilistic guessing.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {AUDIT_FLAGS.map((flag) => (
              <div
                key={flag.code}
                className="neo-card p-5 flex flex-col gap-3 bg-white"
              >
                <div className="flex items-center justify-between">
                  <span className="neo-badge neo-badge-dark">
                    {flag.code} · {flag.label}
                  </span>
                  <span className="neo-badge neo-badge-warm text-[0.65rem]">
                    {flag.tag}
                  </span>
                </div>

                <h3 className="text-lg font-bold text-charcoal mt-1">{flag.title}</h3>
                <p className="text-sm text-charcoal-light leading-relaxed">{flag.desc}</p>

                <div className="mt-auto pt-3 border-t-[1.5px] border-concrete-border flex items-center justify-between text-xs font-mono">
                  <span className="text-concrete font-bold">Basis: {flag.rule}</span>
                  <span className="text-orange font-bold">{flag.metric}</span>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════
          AUDIT COMPARISON — RANDOM SAMPLING VS DEVIATION RANKING
      ═══════════════════════════════════════════════════════════ */}
      <section className="neo-dot-bg border-b-[2.5px] border-charcoal py-16 md:py-20">
        <div className="max-w-7xl mx-auto w-full px-5 flex flex-col gap-10">
          
          <div className="flex flex-col gap-2">
            <span className="neo-badge neo-badge-dark w-fit">EFFICIENCY COMPARISON</span>
            <h2 className="text-3xl md:text-4xl font-bold text-charcoal tracking-tight">
              Why Deviation Ranking Outperforms Random Sampling
            </h2>
            <p className="text-concrete text-base max-w-2xl">
              When oversight resources are scarce, auditing routine tenders wastes time while severe
              deviations remain uninspected.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Traditional Sampling */}
            <div className="neo-card-static p-6 flex flex-col gap-4 bg-beige-alt">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-md bg-charcoal text-white flex items-center justify-center font-bold text-sm">
                  ✕
                </span>
                <h3 className="text-xl font-bold text-charcoal">Traditional Random Sampling</h3>
              </div>
              <ul className="flex flex-col gap-3 text-sm text-charcoal-light">
                <li className="flex items-start gap-2.5">
                  <span className="text-concrete font-bold mt-0.5">•</span>
                  <span><strong>95%+ Routine Contracts:</strong> Most reviewed files are ordinary purchases with zero procedural breaches.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-concrete font-bold mt-0.5">•</span>
                  <span><strong>Equal Selection Probability:</strong> Severe irregularities have the exact same chance of inspection as benign awards.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-concrete font-bold mt-0.5">•</span>
                  <span><strong>Accidental Discoveries:</strong> Irregularities are found only by chance rather than systematic screening.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-concrete font-bold mt-0.5">•</span>
                  <span><strong>No Defensible Priority:</strong> Auditors have no quantitative ranking guiding what should be read first.</span>
                </li>
              </ul>
            </div>

            {/* Anomaly Detection Ranking */}
            <div className="neo-card-orange p-6 flex flex-col gap-4 bg-white">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-md bg-orange text-white flex items-center justify-center font-bold text-sm">
                  ✓
                </span>
                <h3 className="text-xl font-bold text-charcoal">Anomaly Detection Ranking</h3>
              </div>
              <ul className="flex flex-col gap-3 text-sm text-charcoal-light">
                <li className="flex items-start gap-2.5">
                  <span className="text-orange font-bold mt-0.5">•</span>
                  <span><strong>Systematic Screening:</strong> Evaluates 100% of published awards against all 6 statutory rules simultaneously.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-orange font-bold mt-0.5">•</span>
                  <span><strong>The Rank Is The Signal:</strong> Severe multi-flag deviations surface at the very top of the review list.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-orange font-bold mt-0.5">•</span>
                  <span><strong>Defensible Evidence:</strong> Every flag records the underlying quantitative value and statutory legal citation.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-orange font-bold mt-0.5">•</span>
                  <span><strong>Zero Hallucination Risk:</strong> Pure deterministic calculation guarantees consistent, repeatable legal audits.</span>
                </li>
              </ul>
            </div>
          </div>

        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════
          DATA INTEGRITY & TRUST
      ═══════════════════════════════════════════════════════════ */}
      <section className="bg-charcoal text-beige border-b-[2.5px] border-charcoal py-12 md:py-14">
        <div className="max-w-7xl mx-auto w-full px-5 flex flex-col md:flex-row gap-8 items-start md:items-center justify-between">
          <div className="flex flex-col gap-2 max-w-2xl">
            <h3 className="text-2xl font-bold text-white">Data Integrity & Standards</h3>
            <p className="text-sm text-concrete-light leading-relaxed">
              Source data mirrored from <span className="text-orange font-mono font-bold">eprocure.gov.in</span> (Central
              Public Procurement Portal). Loaded slice: six Coal India Limited subsidiaries, 2019–2025.
              Zero LLM was involved in computing risk scores — a mandatory requirement for legal
              and regulatory audit compliance.
            </p>
          </div>
          <div className="flex flex-wrap gap-2 shrink-0">
            <span className="neo-badge neo-badge-dark bg-charcoal-soft">NO LLM IN SCORING</span>
            <span className="neo-badge neo-badge-ghost">SHA-256 VERIFIED</span>
            <span className="neo-badge neo-badge-orange">OPEN SOURCE</span>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════
          FOOTER
      ═══════════════════════════════════════════════════════════ */}
      <footer className="bg-beige py-10">
        <div className="max-w-7xl mx-auto w-full px-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex flex-col gap-1">
            <span className="font-bold text-charcoal text-lg">
              Anomaly Detection · Public Procurement Audit
            </span>
            <span className="text-xs text-concrete font-mono">
              Smart Governance & Compliance · SDG 16 · GFR 2017 Rules
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-5 text-sm font-bold">
            <Link href="/awards" className="text-charcoal-light hover:text-orange transition-colors">
              Review Queue
            </Link>
            <Link href="/awards/demo" className="text-charcoal-light hover:text-orange transition-colors">
              Sample Card
            </Link>
            <a
              href="https://github.com/ekkerihasan/anomaly-detection"
              target="_blank"
              rel="noopener noreferrer"
              className="text-charcoal-light hover:text-orange transition-colors flex items-center gap-1.5"
            >
              <span>GitHub</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </a>
          </div>
        </div>
      </footer>
    </>
  );
}
