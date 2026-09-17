/**
 * Loading placeholder for the App Router `loading.tsx` files.
 */
export default function LoadingState({ label, rows = 6 }: { label: string; rows?: number }) {
  return (
    <main
      className="max-w-5xl mx-auto w-full flex flex-col gap-5 p-6"
      aria-busy="true"
      aria-live="polite"
    >
      <div className="flex items-center gap-3">
        <div className="w-3 h-3 bg-orange rounded-full animate-pulse" />
        <p className="text-base font-bold text-charcoal">{label}</p>
      </div>
      <div className="neo-card-static p-6 flex flex-col gap-3">
        <div className="h-8 w-1/3 rounded-lg bg-beige-alt border-2 border-charcoal/15 animate-pulse" />
        {Array.from({ length: rows }).map((_, i) => (
          <div
            key={i}
            className="h-12 rounded-lg bg-beige-alt border-[1.5px] border-charcoal/10 animate-pulse"
            style={{ animationDelay: `${i * 100}ms`, width: `${100 - i * 5}%` }}
          />
        ))}
      </div>
    </main>
  );
}
