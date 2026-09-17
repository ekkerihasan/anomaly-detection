import { fetchDatasetMeta } from "@/lib/api";

/**
 * Persistent disclosure banner shown whenever the loaded dataset is the dev fixture
 * rather than a live/production slice.
 */
export default async function SyntheticBanner() {
  const meta = await fetchDatasetMeta();
  if (!meta || !meta.synthetic) return null;

  return (
    <div
      role="status"
      className="bg-beige-alt text-charcoal border-b-[2.5px] border-charcoal px-4 py-2.5 text-center text-xs sm:text-sm font-bold tracking-wide font-mono uppercase flex items-center justify-center gap-2"
    >
      <span className="text-orange font-bold text-base">⚠</span>
      <span>SYNTHETIC DEV FIXTURE — generated test data, not real procurement records. Nothing shown here is a finding.</span>
    </div>
  );
}
