import Link from "next/link";
import { OrganisationListItem, ALL_FLAG_CODES, ALL_REVIEW_STATUSES } from "@/types/award";
import { flagLabel, formatOrganisation } from "@/lib/format";

/**
 * Filter bar for the ranked list (plan Section 10, screen 1).
 *
 * A plain GET form, deliberately: filters end up in the URL, which means a
 * demo state is a link. The plan (Section 11, H30-H40) asks for a seeded
 * known-good demo state -- "the exact filters and the exact award that opens
 * on camera" -- and a URL is the least breakable way to hold one.
 */
export default function AwardFilters({
  organisations,
  current,
}: {
  organisations: OrganisationListItem[];
  current: Record<string, string | undefined>;
}) {
  const field = "border border-neutral-300 rounded px-2 py-1.5 text-sm bg-white";
  const label = "flex flex-col gap-1 text-xs font-medium text-neutral-600";

  return (
    <form
      method="GET"
      className="flex flex-wrap items-end gap-3 bg-neutral-50 border border-neutral-200 rounded-lg p-4"
    >
      <label className={label}>
        Organisation
        <select name="organisation_id" defaultValue={current.organisation_id ?? ""} className={field}>
          <option value="">All</option>
          {organisations.map((o) => (
            <option key={o.id} value={o.id}>
              {formatOrganisation(o.name)}
            </option>
          ))}
        </select>
      </label>

      <label className={label}>
        Flag
        <select name="flag_code" defaultValue={current.flag_code ?? ""} className={field}>
          <option value="">Any</option>
          {ALL_FLAG_CODES.map((c) => (
            <option key={c} value={c}>
              {flagLabel(c)}
            </option>
          ))}
        </select>
      </label>

      <label className={label}>
        Review status
        <select name="review_status" defaultValue={current.review_status ?? ""} className={field}>
          <option value="">Any</option>
          {ALL_REVIEW_STATUSES.map((s) => (
            <option key={s} value={s} className="capitalize">
              {s}
            </option>
          ))}
        </select>
      </label>

      <label className={label}>
        Min value (₹)
        <input
          type="number"
          name="min_value"
          defaultValue={current.min_value ?? ""}
          placeholder="0"
          className={`${field} w-32`}
        />
      </label>

      <label className={label}>
        Max value (₹)
        <input
          type="number"
          name="max_value"
          defaultValue={current.max_value ?? ""}
          placeholder="any"
          className={`${field} w-32`}
        />
      </label>

      <label className={label}>
        From
        <input type="date" name="date_from" defaultValue={current.date_from ?? ""} className={field} />
      </label>

      <label className={label}>
        To
        <input type="date" name="date_to" defaultValue={current.date_to ?? ""} className={field} />
      </label>

      <button
        type="submit"
        className="bg-neutral-900 text-white rounded px-4 py-1.5 text-sm font-medium hover:bg-neutral-700"
      >
        Apply
      </button>
      <Link
        href="/awards"
        className="text-sm text-neutral-600 underline px-2 py-1.5 hover:text-neutral-900"
      >
        Reset
      </Link>
    </form>
  );
}
