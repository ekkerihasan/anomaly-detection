import Link from "next/link";
import SyntheticBanner from "@/components/SyntheticBanner";

export default function Home() {
  return (
    <>
      <SyntheticBanner />
      <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans">
        <main className="flex flex-col items-center gap-6 text-center max-w-xl px-6 py-20">
          <h1 className="text-3xl font-semibold tracking-tight text-black">
            Procurement Anomaly Detection
          </h1>
          <p className="text-lg text-zinc-600">
            This does not detect corruption. It ranks tenders by how much they
            deviate from normal procurement behaviour, and shows the auditor
            exactly why — so scarce review time lands on the tenders most worth
            reading.
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            <Link
              href="/awards"
              className="rounded-full bg-black text-white px-5 py-3 font-medium hover:bg-zinc-800"
            >
              Open review queue
            </Link>
            <Link
              href="/awards/demo"
              className="rounded-full border border-zinc-300 px-5 py-3 font-medium hover:bg-white"
            >
              Sample explanation card
            </Link>
          </div>
        </main>
      </div>
    </>
  );
}
