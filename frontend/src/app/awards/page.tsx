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
  open: "bg-neutral-100 text-neutral-700",
  reviewing: "bg-blue-100 text-blue-800",
  referred: "bg-red-100 text-red-800",
  dismissed: "bg-neutral-100 text-neutral-400 line-through",
};

function scoreColor(score: number): string {
  if (score >= 1.8) return "text-red-700";
  if (score >= 1.0) return "text-orange-600";
  return "text-neutral-700";
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
        <main className="max-w-2xl mx-auto p-10 text-center flex flex-col gap-3">
          <h1 className="text-xl font-semibold">API unreachable</h1>
          <p className="text-neutral-600 text-sm">
            The ranked list is served by the FastAPI app. Start it with{" "}
            <code className="bg-neutral-100 px-1.5 py-0.5 rounded font-mono text-xs">
              uvicorn app.main:app --reload
            </code>{" "}
            from <code className="font-mono text-xs">api/</code>, then reload.
          </p>
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
      <main className="max-w-7xl mx-auto w-full flex flex-col gap-5 p-6">
        <header className="flex flex-col gap-1">
          <h1 className="text-2xl font-bold">Review queue</h1>
          <p className="text-neutral-600 text-sm">
            {list.total.toLocaleString("en-IN")} awards carry at least one flag,
            ranked by composite risk score. Read from the top: the rank, not
            the presence of a flag, is the signal. Awards with no flags are not
            listed.
          </p>
        </header>

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

        {list.awards.length === 0 ? (
          <div className="border border-dashed border-neutral-300 rounded-lg p-10 text-center text-neutral-500">
            <p className="font-medium">No awards match these filters.</p>
            <p className="text-sm mt-1">
              Widen the value band or clear the flag filter.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto border border-neutral-200 rounded-lg">
            <table className="w-full text-sm">
              <thead className="bg-neutral-50 text-left text-xs uppercase tracking-wide text-neutral-500">
                <tr>
                  <th className="px-3 py-2 font-medium">Rank</th>
                  <th className="px-3 py-2 font-medium">Score</th>
                  <th className="px-3 py-2 font-medium">Organisation</th>
                  <th className="px-3 py-2 font-medium">Vendor</th>
                  <th className="px-3 py-2 font-medium text-right">Value</th>
                  <th className="px-3 py-2 font-medium">Date</th>
                  <th className="px-3 py-2 font-medium">Flags</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {list.awards.map((a) => (
                  <tr
                    key={a.id}
                    className="border-t border-neutral-100 hover:bg-amber-50/60 transition-colors"
                  >
                    <td className="px-3 py-2 tabular-nums text-neutral-500">#{a.rank}</td>
                    <td className={`px-3 py-2 font-bold tabular-nums ${scoreColor(a.score)}`}>
                      {a.score.toFixed(2)}
                    </td>
                    <td className="px-3 py-2">
                      <Link
                        href={`/awards/${a.id}`}
                        className="font-medium text-blue-800 hover:underline"
                      >
                        {formatOrganisation(a.organisation)}
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-neutral-700">{displayVendor(a.vendor)}</td>
                    <td className="px-3 py-2 text-right tabular-nums">
                      {a.contractValue !== null ? formatInr(a.contractValue) : "—"}
                    </td>
                    <td className="px-3 py-2 text-neutral-600 whitespace-nowrap">
                      {a.contractDate ? formatDate(a.contractDate) : "—"}
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex flex-wrap gap-1">
                        {a.flagCodes.map((c) => (
                          <span
                            key={c}
                            title={c}
                            className="bg-neutral-200 text-neutral-800 rounded px-1.5 py-0.5 text-xs whitespace-nowrap"
                          >
                            {flagLabel(c)}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs capitalize ${STATUS_PILL[a.reviewStatus]}`}
                      >
                        {a.reviewStatus}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {pageCount > 1 && (
          <nav className="flex items-center justify-between text-sm">
            <span className="text-neutral-500">
              Page {page} of {pageCount.toLocaleString("en-IN")}
            </span>
            <div className="flex gap-2">
              {page > 1 && (
                <Link
                  href={qs({ page: String(page - 1) })}
                  className="border border-neutral-300 rounded px-3 py-1 hover:bg-neutral-50"
                >
                  Previous
                </Link>
              )}
              {page < pageCount && (
                <Link
                  href={qs({ page: String(page + 1) })}
                  className="border border-neutral-300 rounded px-3 py-1 hover:bg-neutral-50"
                >
                  Next
                </Link>
              )}
            </div>
          </nav>
        )}
      </main>
    </>
  );
}
