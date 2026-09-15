import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans min-h-screen">
      <main className="flex flex-col items-center gap-6 text-center max-w-lg px-6">
        <h1 className="text-3xl font-semibold tracking-tight text-black">
          Procurement Anomaly Detection
        </h1>
        <p className="text-lg text-zinc-600">
          Ranks government tender awards by how much they deviate from normal
          procurement behaviour, and shows an auditor exactly why.
        </p>
        <Link
          href="/awards/demo"
          className="rounded-full bg-black text-white px-5 py-3 font-medium hover:bg-zinc-800"
        >
          View sample explanation card
        </Link>
      </main>
    </div>
  );
}
