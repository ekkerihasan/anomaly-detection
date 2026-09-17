/**
 * Loading placeholder for the App Router `loading.tsx` files. Plan Section 10
 * lists loading states as non-negotiable: without one, a slow query leaves a
 * blank frame in the screen recording.
 */
export default function LoadingState({ label, rows = 6 }: { label: string; rows?: number }) {
  return (
    <main
      className="max-w-5xl mx-auto w-full flex flex-col gap-4 p-6"
      aria-busy="true"
      aria-live="polite"
    >
      <p className="text-base font-medium text-neutral-700">{label}</p>
      <div className="flex flex-col gap-2 animate-pulse">
        <div className="h-8 w-1/3 rounded bg-neutral-200" />
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-10 rounded bg-neutral-100" />
        ))}
      </div>
    </main>
  );
}
