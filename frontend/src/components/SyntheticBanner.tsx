import { fetchDatasetMeta } from "@/lib/api";

/**
 * Persistent warning shown whenever the loaded dataset is the dev fixture
 * rather than a real slice.
 *
 * MHASH26-BUILD-PLAN.md Section 9 and CLAUDE.md rule 10 both require that
 * anything synthetic is disclosed *on screen*, not just in a README. The
 * state comes from /meta/dataset, which derives it from the data itself --
 * so this cannot be left on by accident after a real load, and cannot be
 * forgotten before a screenshot.
 */
export default async function SyntheticBanner() {
  const meta = await fetchDatasetMeta();
  if (!meta || !meta.synthetic) return null;

  return (
    <div
      role="status"
      className="bg-amber-400 text-amber-950 border-b-2 border-amber-600 px-4 py-2 text-center text-sm font-semibold tracking-wide"
    >
      SYNTHETIC DEV FIXTURE — generated test data, not real procurement
      records. Nothing shown here is a finding.
    </div>
  );
}
