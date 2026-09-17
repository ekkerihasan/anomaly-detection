import Link from "next/link";
import { OrganisationListItem, ALL_FLAG_CODES, ALL_REVIEW_STATUSES } from "@/types/award";
import { flagLabel, formatOrganisation } from "@/lib/format";

/**
 * Filter bar for the ranked list (plan Section 10, screen 1).
 * Plain GET form: preserves filter state in URL parameters.
 */
export default function AwardFilters({
  organisations,
  current,
}: {
  organisations: OrganisationListItem[];
  current: Record<string, string | undefined>;
}) {
  return (
    <form
      method="GET"
      className="neo-card p-5 flex flex-col gap-4 bg-white"
    >
      {/* ── Filter fields ── */}
      <div className="flex flex-wrap items-end gap-3">
        <label className="flex flex-col gap-1.5 text-xs font-bold text-charcoal uppercase tracking-wide">
          Organisation
          <select name="organisation_id" defaultValue={current.organisation_id ?? ""} className="neo-input text-sm min-w-[160px]">
            <option value="">All Organisations</option>
            {organisations.map((o) => (
              <option key={o.id} value={o.id}>
                {formatOrganisation(o.name)}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1.5 text-xs font-bold text-charcoal uppercase tracking-wide">
          Statutory Flag
          <select name="flag_code" defaultValue={current.flag_code ?? ""} className="neo-input text-sm min-w-[150px]">
            <option value="">Any Flag</option>
            {ALL_FLAG_CODES.map((c) => (
              <option key={c} value={c}>
                {flagLabel(c)}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1.5 text-xs font-bold text-charcoal uppercase tracking-wide">
          Review Status
          <select name="review_status" defaultValue={current.review_status ?? ""} className="neo-input text-sm min-w-[130px]">
            <option value="">Any Status</option>
            {ALL_REVIEW_STATUSES.map((s) => (
              <option key={s} value={s} className="capitalize">
                {s}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1.5 text-xs font-bold text-charcoal uppercase tracking-wide">
          Min Value (₹)
          <input
            type="number"
            name="min_value"
            defaultValue={current.min_value ?? ""}
            placeholder="0"
            className="neo-input text-sm w-32"
          />
        </label>

        <label className="flex flex-col gap-1.5 text-xs font-bold text-charcoal uppercase tracking-wide">
          Max Value (₹)
          <input
            type="number"
            name="max_value"
            defaultValue={current.max_value ?? ""}
            placeholder="any"
            className="neo-input text-sm w-32"
          />
        </label>

        <label className="flex flex-col gap-1.5 text-xs font-bold text-charcoal uppercase tracking-wide">
          From Date
          <input type="date" name="date_from" defaultValue={current.date_from ?? ""} className="neo-input text-sm" />
        </label>

        <label className="flex flex-col gap-1.5 text-xs font-bold text-charcoal uppercase tracking-wide">
          To Date
          <input type="date" name="date_to" defaultValue={current.date_to ?? ""} className="neo-input text-sm" />
        </label>
      </div>

      {/* ── Action buttons ── */}
      <div className="flex items-center gap-3 pt-1">
        <button
          type="submit"
          className="neo-btn text-sm py-2 px-5"
        >
          Apply Filters
        </button>
        <Link
          href="/awards"
          className="neo-btn-ghost text-sm py-2 px-4"
        >
          Reset Filters
        </Link>
      </div>
    </form>
  );
}
