import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchOrganisationSummary } from "@/lib/api";
import { formatInr, flagLabel, formatOrganisation, displayVendor } from "@/lib/format";
import SyntheticBanner from "@/components/SyntheticBanner";

// Organisation summary (MHASH26-BUILD-PLAN.md Section 10, screen 3).
// Makes the point that the engine works at aggregate level too, not just
// award by award.

function pct(x: number | null, places = 1): string {
  if (x === null || x === undefined) return "—";
  return `${(x * 100).toFixed(places)}%`;
}

function Stat({
  label,
  value,
  sub,
  emphasis,
}: {
  label: string;
  value: string;
  sub?: string;
  emphasis?: boolean;
}) {
  return (
    <div className="border border-neutral-200 rounded-lg p-4 flex flex-col gap-1">
      <span className="text-xs uppercase tracking-wide text-neutral-500">{label}</span>
      <span
        className={`text-2xl font-bold tabular-nums ${
          emphasis ? "text-red-700" : "text-neutral-900"
        }`}
      >
        {value}
      </span>
      {sub && <span className="text-xs text-neutral-500">{sub}</span>}
    </div>
  );
}

export default async function OrganisationPage({
  params,
}: PageProps<"/organisations/[id]">) {
  const { id } = await params;
  const org = await fetchOrganisationSummary(id);

  if (!org) notFound();

  // March clustering is only interesting relative to an even spread.
  const marchRatio =
    org.lateMarchRate !== null && org.lateMarchBaseline > 0
      ? org.lateMarchRate / org.lateMarchBaseline
      : null;

  return (
    <>
      <SyntheticBanner />
      <main className="max-w-5xl mx-auto w-full flex flex-col gap-6 p-6">
        <nav className="text-sm">
          <Link href="/awards" className="text-blue-800 hover:underline">
            ← Back to review queue
          </Link>
        </nav>

        <header className="flex flex-col gap-1 border-b border-neutral-200 pb-4">
          <h1 className="text-2xl font-bold">{formatOrganisation(org.name)}</h1>
          <p className="text-neutral-600 text-sm">
            {org.awards.toLocaleString("en-IN")} awards ·{" "}
            {formatInr(org.totalValue)} total contracted value
          </p>
        </header>

        <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Stat
            label="Single-bid rate"
            value={pct(org.singleBidRate)}
            sub={`${org.singleBidCount.toLocaleString("en-IN")} awards with one bid`}
            emphasis={(org.singleBidRate ?? 0) > 0.2}
          />
          <Stat
            label="Late-March awards"
            value={pct(org.lateMarchRate)}
            sub={
              marchRatio
                ? `${marchRatio.toFixed(1)}× the ${pct(org.lateMarchBaseline)} even-spread baseline`
                : undefined
            }
            emphasis={(marchRatio ?? 0) > 2}
          />
          <Stat
            label="Median award"
            value={org.medianValue !== null ? formatInr(org.medianValue) : "—"}
            sub={org.maxValue !== null ? `largest ${formatInr(org.maxValue)}` : undefined}
          />
          <Stat
            label="Top vendor share"
            value={pct(org.topVendors[0]?.shareOfValue ?? null)}
            sub="of total contracted value"
          />
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="text-lg font-semibold">Flags raised across this organisation</h2>
          {Object.keys(org.flagCounts).length === 0 ? (
            <p className="text-sm text-neutral-500 border border-dashed border-neutral-300 rounded-lg p-6 text-center">
              No flags raised for this organisation.
            </p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {Object.entries(org.flagCounts).map(([code, n]) => (
                <Link
                  key={code}
                  href={`/awards?organisation_id=${org.id}&flag_code=${code}`}
                  className="border border-neutral-300 rounded-lg px-3 py-2 text-sm hover:bg-neutral-50 flex items-center gap-2"
                >
                  <span className="font-medium">{flagLabel(code)}</span>
                  <span className="tabular-nums text-neutral-500">
                    {n.toLocaleString("en-IN")}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="text-lg font-semibold">Award concentration by vendor</h2>
          {org.topVendors.length === 0 ? (
            <p className="text-sm text-neutral-500">No vendor data.</p>
          ) : (
            <div className="overflow-x-auto border border-neutral-200 rounded-lg">
              <table className="w-full text-sm">
                <thead className="bg-neutral-50 text-left text-xs uppercase tracking-wide text-neutral-500">
                  <tr>
                    <th className="px-3 py-2 font-medium">Vendor (normalised exact name)</th>
                    <th className="px-3 py-2 font-medium text-right">Awards</th>
                    <th className="px-3 py-2 font-medium text-right">Total value</th>
                    <th className="px-3 py-2 font-medium text-right">Share</th>
                  </tr>
                </thead>
                <tbody>
                  {org.topVendors.map((v) => (
                    <tr key={v.vendor} className="border-t border-neutral-100">
                      <td className="px-3 py-2">{displayVendor(v.vendor)}</td>
                      <td className="px-3 py-2 text-right tabular-nums">{v.awards}</td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {formatInr(v.totalValue)}
                      </td>
                      <td className="px-3 py-2 text-right tabular-nums">
                        {pct(v.shareOfValue)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="text-xs text-neutral-500 leading-relaxed bg-neutral-50 border border-neutral-200 rounded p-3">
            {org.caveat}
          </p>
        </section>
      </main>
    </>
  );
}
