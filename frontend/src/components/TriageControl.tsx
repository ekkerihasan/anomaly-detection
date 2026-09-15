"use client";

import { useState } from "react";
import { ReviewStatus } from "@/types/award";

const STATUSES: ReviewStatus[] = ["open", "reviewing", "referred", "dismissed"];

const STATUS_STYLES: Record<ReviewStatus, string> = {
  open: "bg-neutral-100 text-neutral-800 border-neutral-300",
  reviewing: "bg-blue-100 text-blue-800 border-blue-300",
  referred: "bg-red-100 text-red-800 border-red-300",
  dismissed: "bg-neutral-100 text-neutral-500 border-neutral-300 line-through",
};

export default function TriageControl({
  initialStatus,
  initialNote,
}: {
  initialStatus: ReviewStatus;
  initialNote: string | null;
}) {
  const [status, setStatus] = useState<ReviewStatus>(initialStatus);
  const [note, setNote] = useState(initialNote ?? "");

  // Phase 1 scope: local UI state only, against fake data. Wiring this to
  // PATCH /awards/:id/review lands with the real award endpoints (H18-H30
  // per the build plan schedule).

  return (
    <div className="border border-neutral-200 rounded-lg p-4 flex flex-col gap-3">
      <span className="font-semibold text-sm text-neutral-700">Triage</span>
      <div className="flex flex-wrap gap-2">
        {STATUSES.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setStatus(s)}
            className={`px-3 py-1 rounded-full border text-sm capitalize transition-colors ${
              STATUS_STYLES[s]
            } ${status === s ? "ring-2 ring-offset-1 ring-neutral-500" : "opacity-60"}`}
          >
            {s}
          </button>
        ))}
      </div>
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Reviewer note..."
        rows={2}
        className="border border-neutral-200 rounded p-2 text-sm resize-none"
      />
      <p className="text-xs text-neutral-400">
        This is an auditor&apos;s queue, not a verdict.
      </p>
    </div>
  );
}
