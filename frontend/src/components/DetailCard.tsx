import { Award } from "@/types/award";
import { formatInr, formatDate } from "@/lib/format";
import FlagRow from "./FlagRow";
import TriageControl from "./TriageControl";

export default function DetailCard({ award }: { award: Award }) {
  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6 p-6">
      <header className="flex flex-col gap-2 border-b border-neutral-200 pb-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{award.organisation}</h1>
            <p className="text-neutral-600">{award.vendor}</p>
          </div>
          <a
            href={award.detailUrl}
            target="_blank"
            rel="noreferrer"
            className="text-sm text-blue-700 underline shrink-0"
          >
            Original CPPP page
          </a>
        </div>
        <div className="flex flex-wrap gap-x-8 gap-y-1 text-sm text-neutral-700">
          <span>
            <strong>Value:</strong> {formatInr(award.contractValue)}
          </span>
          <span>
            <strong>Date:</strong> {formatDate(award.contractDate)}
          </span>
        </div>
      </header>

      <section className="flex items-baseline gap-4 bg-neutral-900 text-white rounded-lg p-4">
        <span className="text-4xl font-bold tabular-nums">{award.score.toFixed(2)}</span>
        <span className="text-neutral-300">
          risk score &middot; rank #{award.rank} of {award.totalInSlice} in this slice
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

      <TriageControl initialStatus={award.review.status} initialNote={award.review.note} />
    </div>
  );
}
