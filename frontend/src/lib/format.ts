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
