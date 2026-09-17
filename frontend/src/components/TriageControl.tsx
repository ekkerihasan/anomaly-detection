"use client";

import { useState } from "react";
import { ReviewStatus, ALL_REVIEW_STATUSES } from "@/types/award";
import { API_BASE } from "@/lib/api";

const STATUS_STYLES: Record<ReviewStatus, string> = {
  open: "neo-badge neo-badge-ghost cursor-pointer",
  reviewing: "neo-badge bg-concrete text-white cursor-pointer",
  referred: "neo-badge neo-badge-orange cursor-pointer",
  dismissed: "neo-badge bg-beige-dark text-concrete line-through cursor-pointer",
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
  /** Design-reference mode (/awards/demo): interactive, but never writes. */
  readOnly?: boolean;
}) {
  const [status, setStatus] = useState<ReviewStatus>(initialStatus);
  const [note, setNote] = useState(initialNote ?? "");
  const [save, setSave] = useState<SaveState>("idle");

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
    <div className="neo-card p-5 flex flex-col gap-4 bg-white">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm text-charcoal uppercase font-mono tracking-wide">
            Auditor Triage Status
          </span>
          {readOnly && (
            <span className="neo-badge neo-badge-beige text-[0.6rem]">Demo Mode</span>
          )}
        </div>
        <span
          className="text-xs font-mono font-bold h-4"
          aria-live="polite"
          role="status"
        >
          {save === "saving" && <span className="text-concrete">Saving…</span>}
          {save === "saved" && <span className="text-orange">Saved</span>}
          {save === "error" && (
            <span className="text-red-700">Could not save — check API server</span>
          )}
        </span>
      </div>

      <div className="flex flex-wrap gap-2.5">
        {ALL_REVIEW_STATUSES.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => onStatus(s)}
            aria-pressed={status === s}
            className={`px-3.5 py-1.5 rounded-lg border-2 text-xs font-bold uppercase tracking-wide font-mono transition-all ${
              STATUS_STYLES[s]
            } ${
              status === s
                ? "ring-2 ring-orange ring-offset-1 shadow-[3px_3px_0px_#242424]"
                : "opacity-60 hover:opacity-100"
            }`}
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
        placeholder="Record official audit notes or justification here…"
        rows={3}
        className="neo-input text-sm resize-none"
      />

      <p className="text-xs text-concrete font-mono">
        Official auditor queue state — transitions and notes are saved directly to audit history.
      </p>
    </div>
  );
}
