// Mirrors the Postgres schema in db/schema.sql. The frontend only renders
// these shapes — it never computes a score or evaluates flag logic
// (CLAUDE.md rule 5).

export type FlagCode =
  | "F1_SINGLE_BID"
  | "F2_SHORT_WINDOW"
  | "F5_THRESHOLD_BUNCHING"
  | "F9_INSTANT_AWARD"
  | "F11_EMD_ANOMALY"
  | "F12_YEAR_END_RUSH";

export const ALL_FLAG_CODES: FlagCode[] = [
  "F1_SINGLE_BID",
  "F2_SHORT_WINDOW",
  "F5_THRESHOLD_BUNCHING",
  "F9_INSTANT_AWARD",
  "F11_EMD_ANOMALY",
  "F12_YEAR_END_RUSH",
];

export interface Flag {
  code: FlagCode;
  severity: number; // 0..1, computed server-side
  evidence: Record<string, unknown>; // load-bearing JSON the sentence below is built from
  sentence: string; // plain-English explanation, built server-side from evidence
  ruleCitation: string;
}

export type ReviewStatus = "open" | "reviewing" | "referred" | "dismissed";

export const ALL_REVIEW_STATUSES: ReviewStatus[] = [
  "open",
  "reviewing",
  "referred",
  "dismissed",
];

export interface Award {
  id: number;
  organisation: string;
  organisationId: number;
  vendor: string;
  title?: string | null;
  refNo?: string | null;
  tenderType?: string | null;
  contractValue: number;
  contractDate: string; // ISO date
  detailUrl: string;
  score: number;
  rank: number;
  totalInSlice: number;
  flags: Flag[];
  review: {
    status: ReviewStatus;
    note: string | null;
  };
}

/** Row shape returned by the ranked list — lighter than a full Award. */
export interface AwardListItem {
  id: number;
  organisation: string;
  organisationId: number;
  vendor: string;
  contractValue: number | null;
  contractDate: string | null;
  detailUrl: string;
  score: number;
  rank: number;
  reviewStatus: ReviewStatus;
  flagCodes: FlagCode[];
}

export interface AwardListResponse {
  total: number;
  limit: number;
  offset: number;
  awards: AwardListItem[];
}

export interface OrganisationListItem {
  id: number;
  name: string;
  awardCount: number;
}

export interface OrganisationSummary {
  id: number;
  name: string;
  awards: number;
  singleBidRate: number | null;
  singleBidCount: number;
  lateMarchRate: number | null;
  lateMarchCount: number;
  lateMarchBaseline: number;
  totalValue: number;
  medianValue: number | null;
  maxValue: number | null;
  topVendors: {
    vendor: string;
    awards: number;
    totalValue: number;
    shareOfValue: number | null;
  }[];
  flagCounts: Partial<Record<FlagCode, number>>;
  caveat: string;
}

/** Tells the UI whether it is showing the real slice or the dev fixture.
 *  Drives the synthetic-data banner (CLAUDE.md rule 10). */
export interface DatasetMeta {
  synthetic: boolean;
  label: string;
  awards: number;
  scored: number;
}
