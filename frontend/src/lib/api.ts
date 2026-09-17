// Server-side data access for the App Router. The frontend only renders
// what these return -- it never computes a score or evaluates flag logic
// (CLAUDE.md rule 5). Every number on screen was computed in Postgres by
// scripts/compute_flags.py and scripts/compute_scores.py.
import {
  Award,
  AwardListResponse,
  DatasetMeta,
  OrganisationSummary,
  OrganisationListItem,
} from "@/types/award";

export const API_BASE =
  typeof window === "undefined"
    ? process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"
    : process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    // Triage state changes under the user; never serve a cached queue.
    cache: "no-store",
  });
  if (!res.ok) {
    throw new ApiError(res.status, `GET ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

/** Returns null when the API is unreachable, so a page can render a
 *  useful "start the API" empty state instead of a stack trace. */
async function getJsonOrNull<T>(path: string): Promise<T | null> {
  try {
    return await getJson<T>(path);
  } catch {
    return null;
  }
}

export type AwardFilters = {
  organisationId?: string;
  flagCode?: string;
  reviewStatus?: string;
  minValue?: string;
  maxValue?: string;
  dateFrom?: string;
  dateTo?: string;
  limit?: number;
  offset?: number;
};

function toQuery(filters: AwardFilters): string {
  const q = new URLSearchParams();
  if (filters.organisationId) q.set("organisation_id", filters.organisationId);
  if (filters.flagCode) q.set("flag_code", filters.flagCode);
  if (filters.reviewStatus) q.set("review_status", filters.reviewStatus);
  if (filters.minValue) q.set("min_value", filters.minValue);
  if (filters.maxValue) q.set("max_value", filters.maxValue);
  if (filters.dateFrom) q.set("date_from", filters.dateFrom);
  if (filters.dateTo) q.set("date_to", filters.dateTo);
  q.set("limit", String(filters.limit ?? 50));
  q.set("offset", String(filters.offset ?? 0));
  return q.toString();
}

export function fetchAwards(filters: AwardFilters = {}) {
  return getJsonOrNull<AwardListResponse>(`/awards?${toQuery(filters)}`);
}

export function fetchAward(id: string | number) {
  return getJsonOrNull<Award>(`/awards/${id}`);
}

export function fetchOrganisations() {
  return getJsonOrNull<{ organisations: OrganisationListItem[] }>("/organisations");
}

export function fetchOrganisationSummary(id: string | number) {
  return getJsonOrNull<OrganisationSummary>(`/organisations/${id}/summary`);
}

export function fetchDatasetMeta() {
  return getJsonOrNull<DatasetMeta>("/meta/dataset");
}
