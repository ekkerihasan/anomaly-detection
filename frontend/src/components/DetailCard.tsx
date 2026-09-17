import Link from "next/link";
import { Award } from "@/types/award";
import { formatInr, formatDate, formatOrganisation, displayVendor } from "@/lib/format";
import FlagRow from "./FlagRow";
import TriageControl from "./TriageControl";

export default function DetailCard({
  award,
  readOnly = false,
}: {
  award: Award;
  /** Design-reference mode: renders identically but never writes triage state. */
  readOnly?: boolean;
}) {
  return (
    <div className="max-w-4xl mx-auto w-full flex flex-col gap-6 p-5 md:p-8">
      {/* ── Breadcrumb / Back ── */}
      <nav className="flex items-center justify-between">
        <Link
          href="/awards"
          className="neo-btn-ghost text-xs py-2 px-3.5"
        >
          ← Back to Review Queue
        </Link>
        <span className="neo-badge neo-badge-dark text-xs">
          AWARD ID #{award.id}
        </span>
      </nav>

      {/* ── Tender Header Summary Card ── */}
      <header className="neo-card p-6 flex flex-col gap-4 bg-white">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="min-w-0 max-w-2xl">
            <span className="text-xs font-mono font-bold uppercase text-concrete tracking-wide">
              Procuring Entity
            </span>
            <h1 className="text-2xl md:text-3xl font-bold text-charcoal leading-tight">
              <Link
                href={`/organisations/${award.organisationId}`}
                className="hover:text-orange transition-colors"
              >
                {formatOrganisation(award.organisation)}
              </Link>
            </h1>
            <p className="text-base text-concrete font-medium mt-1">
              Vendor: <strong className="text-charcoal">{displayVendor(award.vendor)}</strong>
            </p>
            {award.title && (
              <p className="text-sm text-charcoal-light mt-2 p-3 bg-beige-alt rounded-lg border border-charcoal/10">
                {award.title}
              </p>
            )}
          </div>

          {award.detailUrl && (
            <a
              href={award.detailUrl}
              target="_blank"
              rel="noreferrer"
              className="neo-btn-ghost text-xs py-2 px-3 shrink-0"
            >
              <span>Original CPPP Page</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </a>
          )}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t-[1.5px] border-charcoal/10">
          <div className="flex flex-col">
            <span className="text-xs font-mono uppercase text-concrete font-bold">Contract Value</span>
            <span className="font-mono font-bold text-base text-charcoal">
              {award.contractValue !== null ? formatInr(award.contractValue) : "Not published"}
            </span>
          </div>

          <div className="flex flex-col">
            <span className="text-xs font-mono uppercase text-concrete font-bold">Award Date</span>
            <span className="font-mono font-bold text-sm text-charcoal">
              {award.contractDate ? formatDate(award.contractDate) : "Not published"}
            </span>
          </div>

          {award.refNo && (
            <div className="flex flex-col">
              <span className="text-xs font-mono uppercase text-concrete font-bold">Tender Ref</span>
              <span className="font-mono text-xs text-charcoal truncate" title={award.refNo}>
                {award.refNo}
              </span>
            </div>
          )}

          {award.tenderType && (
            <div className="flex flex-col">
              <span className="text-xs font-mono uppercase text-concrete font-bold">Procurement Type</span>
              <span className="font-semibold text-sm text-charcoal">
                {award.tenderType}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* ── Composite Risk Score Highlight ── */}
      <section className="neo-card p-6 bg-charcoal text-beige flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <span className="text-5xl font-bold font-mono text-orange tabular-nums">
            {award.score.toFixed(2)}
          </span>
          <div className="flex flex-col">
            <span className="font-bold text-base text-white">Composite Deviation Score</span>
            <span className="text-xs font-mono text-concrete-light">
              {award.rank !== null ? (
                <>Rank #{award.rank} of {award.totalInSlice.toLocaleString("en-IN")} flagged awards in slice</>
              ) : (
                <>No statutory flags detected</>
              )}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="neo-badge neo-badge-orange text-xs">
            {award.flags.length} Flag{award.flags.length === 1 ? "" : "s"} Triggered
          </span>
        </div>
      </section>

      {/* ── Statutory Flags Breakdown ── */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-charcoal">
            Statutory Rule Findings ({award.flags.length})
          </h2>
          <span className="text-xs font-mono text-concrete">
            Deterministic Evaluation · GFR 2017 & CVC Rules
          </span>
        </div>

        {award.flags.map((flag) => (
          <FlagRow key={flag.code} flag={flag} />
        ))}
      </section>

      {/* ── Triage Actions ── */}
      <TriageControl
        awardId={award.id}
        initialStatus={award.review.status}
        initialNote={award.review.note}
        readOnly={readOnly}
      />

      {/* ── Legal & Audit Disclaimer ── */}
      <p className="text-xs text-concrete leading-relaxed font-mono p-4 bg-beige-alt rounded-xl border border-charcoal/10">
        Note for Reviewing Auditors: This composite score ranks deviation from standard
        procurement behavior within the loaded dataset slice. It is an algorithmic audit prioritization tool,
        not a judicial determination of corruption. Zero language models were used in computing any score;
        every finding is derived via deterministic SQL rules over published CPPP filings.
      </p>
    </div>
  );
}
