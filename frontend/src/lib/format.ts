export function formatInr(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(iso));
}

const FLAG_LABELS: Record<string, string> = {
  F1_SINGLE_BID: "Single bid",
  F2_SHORT_WINDOW: "Short bid window",
  F5_THRESHOLD_BUNCHING: "Threshold bunching",
  F9_INSTANT_AWARD: "Instant award",
  F11_EMD_ANOMALY: "EMD anomaly",
  F12_YEAR_END_RUSH: "Year-end rush",
};

export function flagLabel(code: string): string {
  return FLAG_LABELS[code] ?? code;
}

/**
 * Raw CPPP organisation names carry the sub-unit after "||"
 * ("Central Coalfields Limited||Kathara"). Display-only: the grouping and
 * every organisation-level statistic are unchanged.
 */
export function formatOrganisation(name: string | null | undefined): string {
  if (!name) return "—";
  return name
    .split("||")
    .map((part) => part.trim())
    .filter(Boolean)
    .join(" · ");
}

/**
 * Vendor names on screen, redacted when REDACT_VENDORS=1 is set on the
 * Next.js server (MHASH26-BUILD-PLAN.md Section 10 and Section 14: no real
 * firm's name next to the word "risk" in a recorded or published artefact).
 *
 * Redaction is a stable short code derived from the name, so the same vendor
 * keeps the same code across screens and concentration is still visible on
 * camera. It is a display mask for recordings, not anonymisation: the API
 * still returns real names.
 */
export function displayVendor(name: string | null | undefined): string {
  if (!name) return "—";
  if (process.env.REDACT_VENDORS !== "1") return name;
  const key = name.trim().replace(/\s+/g, " ").toUpperCase();
  let h = 0x811c9dc5;
  for (let i = 0; i < key.length; i++) {
    h ^= key.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return `Vendor ${h.toString(16).toUpperCase().padStart(8, "0").slice(0, 6)}`;
}
