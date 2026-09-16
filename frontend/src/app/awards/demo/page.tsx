import DetailCard from "@/components/DetailCard";
import { fakeAward } from "@/lib/fakeData";

// Design reference: the detail/explanation card against hardcoded fake JSON,
// per MHASH26-BUILD-PLAN.md Section 10 ("design it at H0 against fake JSON").
// The real page now lives at /awards/[id]. This one is kept because it renders
// without a database or API, which makes it the safe fallback if the demo box
// loses its backend mid-presentation.
//
// readOnly is load-bearing: without it, clicking a triage button here would
// PUT review state onto whichever real award happens to share fakeAward.id.
export default function DemoAwardPage() {
  return (
    <>
      <div
        role="status"
        className="bg-neutral-800 text-neutral-100 px-4 py-2 text-center text-sm"
      >
        Design reference — hardcoded sample data, triage disabled. The live
        queue is at <code className="font-mono">/awards</code>.
      </div>
      <DetailCard award={fakeAward} readOnly />
    </>
  );
}
