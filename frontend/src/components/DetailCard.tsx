import Link from "next/link";
import { Award } from "@/types/award";
import { formatInr, formatDate, formatOrganisation, displayVendor } from "@/lib/format";
import FlagRow from "./FlagRow";
import TriageControl from "./TriageControl";

// Detail / explanation card (MHASH26-BUILD-PLAN.md Section 10, screen 2).
// The highest-value component in the build: every sentence below is built
// server-side from the flag's `evidence` blob, and the raw numbers are shown
// next to the prose so an auditor can check the claim rather than trust it.

export default function DetailCard({
  award,
  readOnly = false,
}: {
  award: Award;
  /** Design-reference mode: renders identically but never writes triage state. */
  readOnly?: boolean;
}) {
  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6 p-6">
      <nav className="text-sm">
        <Link href="/awards" className="text-blue-800 hover:underline">
          ← Back to review queue
        </Link>
      </nav>

      <header className="flex flex-col gap-2 border-b border-neutral-200 pb-4">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <h1 className="text-2xl font-bold">
              <Link
                href={`/organisations/${award.organisationId}`}
                className="hover:underline"
              >
                {formatOrganisation(award.organisation)}
              </Link>
            </h1>
            <p className="text-neutral-600">{displayVendor(award.vendor)}</p>
            {award.title && (
              <p className="text-sm text-neutral-500 mt-1">{award.title}</p>
            )}
          </div>
          {award.detailUrl && (
            <a
              href={award.detailUrl}
              target="_blank"
              rel="noreferrer"
              className="text-sm text-blue-700 underline shrink-0"
            >
              Original CPPP page
            </a>
          )}
        </div>
        <div className="flex flex-wrap gap-x-8 gap-y-1 text-sm text-neutral-700">
          <span>
            <strong>Value:</strong>{" "}
            {award.contractValue !== null ? formatInr(award.contractValue) : "not published"}
          </span>
          <span>
            <strong>Date:</strong>{" "}
            {award.contractDate ? formatDate(award.contractDate) : "not published"}
          </span>
          {award.refNo && (
            <span>
              <strong>Ref:</strong>{" "}
              <span className="font-mono text-xs">{award.refNo}</span>
            </span>
          )}
          {award.tenderType && (
            <span>
              <strong>Type:</strong> {award.tenderType}
            </span>
          )}
        </div>
      </header>

      <section className="flex items-baseline gap-4 bg-neutral-900 text-white rounded-lg p-4">
        <span className="text-4xl font-bold tabular-nums">{award.score.toFixed(2)}</span>
        <span className="text-neutral-300">
          {award.rank !== null ? (
            <>
              risk score &middot; rank #{award.rank} of{" "}
              {award.totalInSlice.toLocaleString("en-IN")} flagged awards in this slice
            </>
          ) : (
            <>no flags raised &middot; not in the review queue</>
          )}
        </span>
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">
          {award.flags.length} flag{award.flags.length === 1 ? "" : "s"} raised
        </h2>
        {award.flags.map((flag) => (
          <FlagRow key={flag.code} flag={flag} />
        ))}
      </section>

      <TriageControl
        awardId={award.id}
        initialStatus={award.review.status}
        initialNote={award.review.note}
        readOnly={readOnly}
      />

      <p className="text-xs text-neutral-500 leading-relaxed border-t border-neutral-200 pt-4">
        This score ranks deviation from normal procurement behaviour within the
        loaded slice. It is not a finding of wrongdoing, and it is not a
        national percentile. No language model was involved in computing any
        flag, severity or score — every number above came from a deterministic
        SQL rule over published CPPP fields.
      </p>
    </div>
  );
}
