import { Flag } from "@/types/award";
import { flagLabel } from "@/lib/format";

function severityColor(severity: number): string {
  if (severity >= 0.8) return "bg-red-600";
  if (severity >= 0.5) return "bg-orange-500";
  return "bg-yellow-500";
}

export default function FlagRow({ flag }: { flag: Flag }) {
  return (
    <div className="border border-neutral-200 rounded-lg p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span
            className={`inline-block w-3 h-3 rounded-full ${severityColor(flag.severity)}`}
            aria-hidden
          />
          <span className="font-semibold text-lg">{flagLabel(flag.code)}</span>
          <span className="text-xs text-neutral-500 font-mono">{flag.code}</span>
        </div>
        <span className="text-sm font-mono text-neutral-600">
          severity {flag.severity.toFixed(2)}
        </span>
      </div>

      <p className="text-base leading-snug">{flag.sentence}</p>

      <dl className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1 text-sm text-neutral-700 bg-neutral-50 rounded p-3 mt-1">
        {Object.entries(flag.evidence).map(([key, value]) => (
          <div key={key} className="flex flex-col">
            <dt className="text-neutral-500 font-mono text-xs">{key}</dt>
            <dd className="font-medium">{String(value)}</dd>
          </div>
        ))}
      </dl>

      <p className="text-xs text-neutral-500 italic">{flag.ruleCitation}</p>
    </div>
  );
}
