import { useEffect, useState } from "react";

const LOADING_STAGES = [
  "Searching indexed documents…",
  "Ranking relevant sources…",
  "Generating grounded answer…",
] as const;

const STAGE_INTERVAL_MS = 2200;

export function LoadingState() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setStageIndex((current) => (current + 1) % LOADING_STAGES.length);
    }, STAGE_INTERVAL_MS);

    return () => window.clearInterval(timer);
  }, []);

  return (
    <div
      className="flex items-center gap-2.5 px-0.5 py-3 text-ink-secondary"
      role="status"
      aria-live="polite"
    >
      <span
        className="h-1.5 w-1.5 shrink-0 rounded-full bg-accent animate-[pulse-dot_1.2s_ease-in-out_infinite]"
        aria-hidden="true"
      />
      <p className="m-0 text-[0.875rem] leading-snug">{LOADING_STAGES[stageIndex]}</p>
    </div>
  );
}
