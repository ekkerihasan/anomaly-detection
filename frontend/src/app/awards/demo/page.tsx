import DetailCard from "@/components/DetailCard";
import { fakeAward } from "@/lib/fakeData";

// Phase 1 scope: renders the detail/explanation card against hardcoded
// fake JSON, per MHASH26-BUILD-PLAN.md Section 10 ("design it at H0
// against fake JSON, before real data exists"). Swaps to a real
// /awards/:id fetch once the award API endpoints exist.
export default function DemoAwardPage() {
  return <DetailCard award={fakeAward} />;
}
