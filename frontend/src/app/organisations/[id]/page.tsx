import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchOrganisationSummary } from "@/lib/api";
import { formatInr, flagLabel, formatOrganisation, displayVendor } from "@/lib/format";
import SyntheticBanner from "@/components/SyntheticBanner";

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
    <div className={`neo-card p-4 flex flex-col gap-1 bg-white ${emphasis ? "border-orange" : ""}`}>
      <span className="text-xs font-mono uppercase tracking-wide text-concrete font-bold">{label}</span>
      <span
        className={`text-2xl font-bold font-mono tabular-nums ${
          emphasis ? "text-orange" : "text-charcoal"
        }`}
      >
        {value}
      </span>
      {sub && <span className="text-xs text-concrete font-mono">{sub}</span>}
    </div>
  );
}

export default async function OrganisationPage({
  params,
}: PageProps<"/organisations/[id]">) {
  const { id } = await params;
  const org = await fetchOrganisationSummary(id);

  if (!org) notFound();

  // March clustering relative to an even spread
  const marchRatio =
    org.lateMarchRate !== null && org.lateMarchBaseline > 0
      ? org.lateMarchRate / org.lateMarchBaseline
      : null;

  return (
    <>
      <SyntheticBanner />
      <main className="max-w-5xl mx-auto w-full flex flex-col gap-6 p-5 md:p-8">
        <nav className="flex items-center justify-between">
          <Link href="/awards" className="neo-btn-ghost text-xs py-2 px-3.5">
            ← Back to Review Queue
          </Link>
          <span className="neo-badge neo-badge-dark text-xs">
            ORGANISATION PROFILE
          </span>
        </nav>

        <header className="neo-card p-6 flex flex-col gap-2 bg-white">
          <span className="text-xs font-mono font-bold uppercase text-concrete tracking-wide">
            Public Procurement Entity
          </span>
          <h1 className="text-2xl md:text-3xl font-bold text-charcoal">{formatOrganisation(org.name)}</h1>
          <p className="text-concrete text-sm font-mono">
            {org.awards.toLocaleString("en-IN")} awards analyzed ·{" "}
            {formatInr(org.totalValue)} total contracted volume
          </p>
        </header>

        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Stat
            label="Single-bid rate"
            value={pct(org.singleBidRate)}
            sub={`${org.singleBidCount.toLocaleString("en-IN")} awards with 1 bid`}
            emphasis={(org.singleBidRate ?? 0) > 0.2}
          />
          <Stat
            label="Late-March awards"
            value={pct(org.lateMarchRate)}
            sub={
              marchRatio
                ? `${marchRatio.toFixed(1)}× the ${pct(org.lateMarchBaseline)} baseline`
                : undefined
            }
            emphasis={(marchRatio ?? 0) > 2}
          />
          <Stat
            label="Median award"
            value={org.medianValue !== null ? formatInr(org.medianValue) : "—"}
            sub={org.maxValue !== null ? `Max ${formatInr(org.maxValue)}` : undefined}
          />
          <Stat
            label="Top vendor share"
            value={pct(org.topVendors[0]?.shareOfValue ?? null)}
            sub="of total contracted value"
          />
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="text-lg font-bold text-charcoal">Statutory Flags Triggered in this Entity</h2>
          {Object.keys(org.flagCounts).length === 0 ? (
            <p className="text-sm text-concrete neo-card p-6 text-center bg-white">
              No statutory red flags raised for this organisation.
            </p>
          ) : (
            <div className="flex flex-wrap gap-2.5">
              {Object.entries(org.flagCounts).map(([code, n]) => (
                <Link
                  key={code}
                  href={`/awards?organisation_id=${org.id}&flag_code=${code}`}
                  className="neo-card-subtle px-4 py-2.5 text-sm hover:border-orange flex items-center gap-2.5 transition-all bg-white"
                >
                  <span className="neo-badge neo-badge-dark text-xs">{code}</span>
                  <span className="font-bold text-charcoal">{flagLabel(code)}</span>
                  <span className="neo-badge neo-badge-warm text-xs font-mono">
                    {n.toLocaleString("en-IN")}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="flex flex-col gap-3">
          <h2 className="text-lg font-bold text-charcoal">Vendor Concentration Analysis</h2>
          {org.topVendors.length === 0 ? (
            <p className="text-sm text-concrete neo-card p-6 text-center bg-white">No vendor distribution data available.</p>
          ) : (
            <div className="neo-table-wrap overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-charcoal text-beige text-left text-xs uppercase tracking-wider font-mono">
                  <tr>
                    <th className="px-4 py-3 font-bold">Vendor (Exact Normalised Identity)</th>
                    <th className="px-4 py-3 font-bold text-right">Award Count</th>
                    <th className="px-4 py-3 font-bold text-right">Contracted Value</th>
                    <th className="px-4 py-3 font-bold text-right">Volume Share</th>
                  </tr>
                </thead>
                <tbody>
                  {org.topVendors.map((v, i) => (
                    <tr
                      key={v.vendor}
                      className={`border-t-[1.5px] border-charcoal/10 transition-colors hover:bg-orange/5 ${
                        i % 2 === 0 ? "bg-white" : "bg-beige/40"
                      }`}
                    >
                      <td className="px-4 py-3 font-medium text-charcoal">{displayVendor(v.vendor)}</td>
                      <td className="px-4 py-3 text-right tabular-nums font-mono text-concrete">{v.awards}</td>
                      <td className="px-4 py-3 text-right tabular-nums font-mono font-semibold text-charcoal">
                        {formatInr(v.totalValue)}
                      </td>
                      <td className="px-4 py-3 text-right tabular-nums font-mono font-bold text-orange">
                        {pct(v.shareOfValue)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="text-xs text-concrete font-mono leading-relaxed bg-beige-alt border border-charcoal/10 rounded-xl p-3.5">
            {org.caveat}
          </p>
        </section>
      </main>
    </>
  );
}
