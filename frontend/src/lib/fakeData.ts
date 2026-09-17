// Hardcoded fake data for building the detail/explanation card before real
// data exists (MHASH26-BUILD-PLAN.md Section 10: "Design it at H0 against
// fake JSON"). Vendor/organisation names below are fictitious placeholders,
// not drawn from any real CPPP record.
import { Award } from "@/types/award";

export const fakeAward: Award = {
  id: 1,
  organisation: "State Public Works Division (sample org)",
  organisationId: 0,
  vendor: "M/S Sample Electricals Pvt Ltd",
  contractValue: 4975000,
  contractDate: "2024-03-27",
  detailUrl: "https://eprocure.gov.in/",
  score: 3.27,
  rank: 1,
  totalInSlice: 1247,
  flags: [
    {
      code: "F1_SINGLE_BID",
      severity: 0.7,
      evidence: { bids_received: 1, tender_type: "Open Tender", peer_median_bids: 4.2 },
      sentence:
        "Only one bid was received. Comparable tenders in this category averaged 4.2 bids.",
      ruleCitation: "GFR competition principle, OCP red flag 1",
    },
    {
      code: "F2_SHORT_WINDOW",
      severity: 0.89,
      evidence: {
        window_days: 9,
        required_days: 21,
        epublished_date: "2024-03-10",
        bid_end_date: "2024-03-19",
      },
      sentence: "The bid window was 9 days. GFR Rule 161 requires 21 days for an advertised tender enquiry.",
      ruleCitation: "GFR 2017 Rule 161",
    },
    {
      code: "F5_THRESHOLD_BUNCHING",
      severity: 1.0,
      evidence: {
        contract_value: 4975000,
        threshold: 5000000,
        gap_pct: 0.005,
        rule: "GFR Rule 162 - limited tender enquiry up to Rs 50 lakh",
      },
      sentence:
        "The contract value sits 0.5% below the Rs 50 lakh limited-tender-enquiry threshold, just inside the band that avoids the next level of procedural scrutiny.",
      ruleCitation: "GFR Rule 162 - limited tender enquiry up to Rs 50 lakh",
    },
    {
      code: "F11_EMD_ANOMALY",
      severity: 0.75,
      evidence: {
        emd: 497500,
        contract_value: 4975000,
        ratio: 0.1,
        peer_ratio_median: 0.02,
      },
      sentence:
        "The earnest money deposit is 10% of the contract value, against a 2% median for this organisation -- high enough to be gatekeeping who can even bid.",
      ruleCitation: "GFR EMD norms",
    },
    {
      code: "F9_INSTANT_AWARD",
      severity: 1.0,
      evidence: {
        decision_days: 0,
        bid_open_date: "2024-03-20",
        contract_date: "2024-03-20",
        peer_median_days: 5,
      },
      sentence:
        "The award was made the same day bids were opened, with no measurable evaluation period. Comparable tenders in this organisation took 5 days.",
      ruleCitation: "OCP red flag, decision period",
    },
    {
      code: "F12_YEAR_END_RUSH",
      severity: 0.4,
      evidence: {
        contract_date: "2024-03-27",
        org_march_share: 0.34,
        org_annual_share: 0.083,
      },
      sentence:
        "This award was made in the last two weeks of March. This organisation makes 34% of its annual awards in that window, against a baseline share of 8.3% if awards were spread evenly across the year.",
      ruleCitation: "Standard audit practice, year-end clustering",
    },
  ],
  review: {
    status: "open",
    note: null,
  },
};
