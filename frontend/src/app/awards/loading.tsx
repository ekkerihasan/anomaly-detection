import LoadingState from "@/components/LoadingState";

export default function Loading() {
  return <LoadingState label="Loading ranked review queue…" rows={10} />;
}
