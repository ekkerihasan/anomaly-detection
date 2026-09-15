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

export interface Flag {
  code: FlagCode;
  severity: number; // 0..1, computed server-side
  evidence: Record<string, unknown>; // load-bearing JSON the sentence below is built from
  sentence: string; // plain-English explanation, built server-side from evidence
  ruleCitation: string;
}

export type ReviewStatus = "open" | "reviewing" | "referred" | "dismissed";

export interface Award {
  id: number;
  organisation: string;
  vendor: string;
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
