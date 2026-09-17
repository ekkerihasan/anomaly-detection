import Link from "next/link";
import { fetchAwards, fetchOrganisations } from "@/lib/api";
import { formatInr, formatDate, flagLabel, formatOrganisation, displayVendor } from "@/lib/format";
import AwardFilters from "@/components/AwardFilters";
import SyntheticBanner from "@/components/SyntheticBanner";
import { ReviewStatus } from "@/types/award";

// Ranked list (MHASH26-BUILD-PLAN.md Section 10, screen 1). Server
// component: the ordering and every score arrive precomputed from the API.

const PAGE_SIZE = 50;

const STATUS_PILL: Record<ReviewStatus, string> = {
  open: "neo-badge neo-badge-ghost",
  reviewing: "neo-badge bg-concrete text-white",
  referred: "neo-badge neo-badge-orange",
  dismissed: "neo-badge bg-beige-dark text-concrete line-through",
};

function scoreColor(score: number): string {
  if (score >= 1.8) return "text-white bg-orange";
  if (score >= 1.0) return "text-charcoal bg-beige-dark font-bold";
  return "text-charcoal bg-beige-alt";
}

export default async function AwardsPage({
  searchParams,
}: PageProps<"/awards">) {
  const sp = await searchParams;
  const one = (k: string) => {
    const v = sp[k];
    return Array.isArray(v) ? v[0] : v;
  };

  const page = Math.max(1, Number(one("page") ?? 1) || 1);
  const offset = (page - 1) * PAGE_SIZE;

  const [list, orgs] = await Promise.all([
    fetchAwards({
      organisationId: one("organisation_id"),
      flagCode: one("flag_code"),
      reviewStatus: one("review_status"),
      minValue: one("min_value"),
      maxValue: one("max_value"),
      dateFrom: one("date_from"),
      dateTo: one("date_to"),
      limit: PAGE_SIZE,
      offset,
    }),
    fetchOrganisations(),
  ]);

  if (!list) {
    return (
      <>
        <SyntheticBanner />
        <main className="max-w-3xl mx-auto p-10 text-center flex flex-col gap-5 items-center">
          <div className="neo-card p-8 flex flex-col gap-3 items-center bg-white">
            <span className="text-3xl text-orange">⚠</span>
            <h1 className="text-xl font-bold text-charcoal">API Unreachable</h1>
            <p className="text-concrete text-sm max-w-md">
              The ranked list is served by the FastAPI app. Ensure it is running
              at <code className="font-mono text-xs font-bold text-charcoal">localhost:8000</code>, then reload this page.
            </p>
          </div>
        </main>
      </>
    );
  }

  const pageCount = Math.max(1, Math.ceil(list.total / PAGE_SIZE));
  const qs = (overrides: Record<string, string>) => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(sp)) {
      const val = Array.isArray(v) ? v[0] : v;
      if (val) q.set(k, val);
    }
    for (const [k, v] of Object.entries(overrides)) q.set(k, v);
    return `?${q.toString()}`;
  };

  return (
    <>
      <SyntheticBanner />
      <main className="max-w-7xl mx-auto w-full flex flex-col gap-6 p-5 md:p-8">
        {/* ── Header ── */}
        <header className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-bold text-charcoal tracking-tight">
              Audit Review Queue
            </h1>
            <span className="neo-badge neo-badge-dark">
              {list.total.toLocaleString("en-IN")} FLAGGED AWARDS
            </span>
            <span className="neo-badge neo-badge-ghost text-xs">
              GFR 2017 & CVC RULES
            </span>
          </div>
          <p className="text-sm text-concrete max-w-3xl leading-relaxed">
            Every tender award below triggered at least one statutory procurement red flag.
            Awards are ranked in descending order of composite deviation score — begin review from
            the top of the list.
          </p>
        </header>

        {/* ── Filters ── */}
        <AwardFilters
          organisations={orgs?.organisations ?? []}
          current={{
            organisation_id: one("organisation_id"),
            flag_code: one("flag_code"),
            review_status: one("review_status"),
            min_value: one("min_value"),
            max_value: one("max_value"),
            date_from: one("date_from"),
            date_to: one("date_to"),
          }}
        />

        {/* ── Table ── */}
        {list.awards.length === 0 ? (
          <div className="neo-card-static p-10 text-center flex flex-col gap-2 items-center bg-white">
            <span className="text-3xl">🔍</span>
            <p className="font-bold text-charcoal">No awards match these filter criteria.</p>
            <p className="text-sm text-concrete">
              Try widening the value band or clearing the selected flag filter.
            </p>
          </div>
        ) : (
          <div className="neo-table-wrap overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-charcoal text-beige text-left text-xs uppercase tracking-wider font-mono">
                  <th className="px-4 py-3 font-bold">Rank</th>
                  <th className="px-4 py-3 font-bold">Risk Score</th>
                  <th className="px-4 py-3 font-bold">Organisation</th>
                  <th className="px-4 py-3 font-bold">Vendor</th>
                  <th className="px-4 py-3 font-bold text-right">Value (₹)</th>
                  <th className="px-4 py-3 font-bold">Date</th>
                  <th className="px-4 py-3 font-bold">Flags</th>
                  <th className="px-4 py-3 font-bold">Status</th>
                </tr>
              </thead>
              <tbody>
                {list.awards.map((a, i) => (
                  <tr
                    key={a.id}
                    className={`border-t-[1.5px] border-charcoal/10 transition-colors hover:bg-orange/5 ${
                      i % 2 === 0 ? "bg-white" : "bg-beige/40"
                    }`}
                  >
                    <td className="px-4 py-3 font-mono font-bold text-concrete tabular-nums">
                      #{a.rank}
                    </td>
                    <td className="px-4 py-3">
                      <span className={`neo-badge font-mono ${scoreColor(a.score)}`}>
                        {a.score.toFixed(2)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link
                        href={`/awards/${a.id}`}
                        className="font-semibold text-charcoal hover:text-orange transition-colors underline decoration-1 underline-offset-2 decoration-charcoal/20 hover:decoration-orange"
                      >
                        {formatOrganisation(a.organisation)}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-concrete text-sm">{displayVendor(a.vendor)}</td>
                    <td className="px-4 py-3 text-right font-mono tabular-nums font-semibold text-charcoal">
                      {a.contractValue !== null ? formatInr(a.contractValue) : "—"}
                    </td>
                    <td className="px-4 py-3 text-concrete whitespace-nowrap font-mono text-xs">
                      {a.contractDate ? formatDate(a.contractDate) : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {a.flagCodes.map((c) => (
                          <span
                            key={c}
                            title={c}
                            className="neo-badge neo-badge-warm text-[0.65rem]"
                          >
                            {flagLabel(c)}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`${STATUS_PILL[a.reviewStatus]} text-[0.65rem] capitalize`}>
                        {a.reviewStatus}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ── Pagination ── */}
        {pageCount > 1 && (
          <nav className="flex items-center justify-between pt-2">
            <span className="text-sm font-mono font-bold text-concrete">
              Page {page} of {pageCount.toLocaleString("en-IN")}
            </span>
            <div className="flex gap-2">
              {page > 1 && (
                <Link
                  href={qs({ page: String(page - 1) })}
                  className="neo-btn-ghost text-sm py-2 px-4"
                >
                  ← Previous
                </Link>
              )}
              {page < pageCount && (
                <Link
                  href={qs({ page: String(page + 1) })}
                  className="neo-btn-ghost text-sm py-2 px-4"
                >
                  Next →
                </Link>
              )}
            </div>
          </nav>
        )}
      </main>
    </>
  );
}
