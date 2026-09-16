"use client";

import { useState } from "react";
import { ReviewStatus, ALL_REVIEW_STATUSES } from "@/types/award";
import { API_BASE } from "@/lib/api";

const STATUS_STYLES: Record<ReviewStatus, string> = {
  open: "bg-neutral-100 text-neutral-800 border-neutral-300",
  reviewing: "bg-blue-100 text-blue-800 border-blue-300",
  referred: "bg-red-100 text-red-800 border-red-300",
  dismissed: "bg-neutral-100 text-neutral-500 border-neutral-300 line-through",
};

type SaveState = "idle" | "saving" | "saved" | "error";

export default function TriageControl({
  awardId,
  initialStatus,
  initialNote,
  readOnly = false,
}: {
  awardId: number;
  initialStatus: ReviewStatus;
  initialNote: string | null;
  /** Design-reference mode (/awards/demo): interactive, but never writes.
   *  Without this the demo card would PUT triage state onto a real award. */
  readOnly?: boolean;
}) {
  const [status, setStatus] = useState<ReviewStatus>(initialStatus);
  const [note, setNote] = useState(initialNote ?? "");
  const [save, setSave] = useState<SaveState>("idle");

  // Persists to PUT /awards/:id/review. The triage state lives in Postgres,
  // not in component state -- a queue that forgets what you referred is not
  // an audit tool.
  async function persist(nextStatus: ReviewStatus, nextNote: string) {
    if (readOnly) return;
    setSave("saving");
    try {
      const res = await fetch(`${API_BASE}/awards/${awardId}/review`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus, note: nextNote || null }),
      });
      setSave(res.ok ? "saved" : "error");
    } catch {
      setSave("error");
    }
  }

  function onStatus(s: ReviewStatus) {
    setStatus(s);
    void persist(s, note);
  }

  return (
    <div className="border border-neutral-200 rounded-lg p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="font-semibold text-sm text-neutral-700">Triage</span>
        <span
          className="text-xs h-4"
          aria-live="polite"
          role="status"
        >
          {save === "saving" && <span className="text-neutral-400">Saving…</span>}
          {save === "saved" && <span className="text-green-700">Saved</span>}
          {save === "error" && (
            <span className="text-red-700">Could not save — is the API running?</span>
          )}
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        {ALL_REVIEW_STATUSES.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => onStatus(s)}
            aria-pressed={status === s}
            className={`px-3 py-1 rounded-full border text-sm capitalize transition-colors ${
              STATUS_STYLES[s]
            } ${status === s ? "ring-2 ring-offset-1 ring-neutral-500" : "opacity-60 hover:opacity-100"}`}
          >
            {s}
          </button>
        ))}
      </div>

      <textarea
        value={note}
        onChange={(e) => {
          setNote(e.target.value);
          setSave("idle");
        }}
        onBlur={() => void persist(status, note)}
        placeholder="Reviewer note…"
        rows={2}
        className="border border-neutral-200 rounded p-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-neutral-400"
      />

      <p className="text-xs text-neutral-400">
        This is an auditor&apos;s queue, not a verdict.
      </p>
    </div>
  );
}
