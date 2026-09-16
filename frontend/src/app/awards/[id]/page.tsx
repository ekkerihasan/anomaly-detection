import { notFound } from "next/navigation";
import DetailCard from "@/components/DetailCard";
import SyntheticBanner from "@/components/SyntheticBanner";
import { fetchAward } from "@/lib/api";

// Real detail page. Replaces the hardcoded-JSON version at /awards/demo,
// which stays in the repo as the design reference the plan asked for
// (Section 10: "design it at H0 against fake JSON").

export default async function AwardDetailPage({
  params,
}: PageProps<"/awards/[id]">) {
  const { id } = await params;
  const award = await fetchAward(id);

  if (!award) notFound();

  return (
    <>
      <SyntheticBanner />
      <DetailCard award={award} />
    </>
  );
}
