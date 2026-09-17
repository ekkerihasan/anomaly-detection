import { Flag } from "@/types/award";
import { flagLabel } from "@/lib/format";

function severityBadge(severity: number) {
  if (severity >= 0.8) return "neo-badge neo-badge-orange";
  if (severity >= 0.5) return "neo-badge neo-badge-dark";
  return "neo-badge neo-badge-ghost";
}

export default function FlagRow({ flag }: { flag: Flag }) {
  return (
    <div className="neo-card p-5 flex flex-col gap-3 bg-white">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <span className="neo-badge neo-badge-dark font-mono text-xs">
            {flag.code}
          </span>
          <span className="font-bold text-lg text-charcoal">{flagLabel(flag.code)}</span>
        </div>
        <span className={`font-mono text-xs ${severityBadge(flag.severity)}`}>
          Severity {flag.severity.toFixed(2)}
        </span>
      </div>

      <p className="text-base text-charcoal-light leading-snug">{flag.sentence}</p>

      <dl className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-2 text-sm text-charcoal bg-beige-alt rounded-lg border border-charcoal/10 p-3.5 mt-1">
        {Object.entries(flag.evidence).map(([key, value]) => (
          <div key={key} className="flex flex-col">
            <dt className="text-concrete font-mono text-xs uppercase">{key}</dt>
            <dd className="font-bold font-mono text-charcoal tabular-nums">
              {value === null ? "—" : String(value)}
            </dd>
          </div>
        ))}
      </dl>

      <div className="pt-1 text-xs font-mono text-concrete">
        <strong className="text-charcoal">Statutory Basis:</strong> {flag.ruleCitation}
      </div>
    </div>
  );
}
