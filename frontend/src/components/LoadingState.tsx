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
        <div className="loading-state" role="status" aria-live="polite">
            <span className="loading-state__indicator" aria-hidden="true" />
            <p className="loading-state__text">{LOADING_STAGES[stageIndex]}</p>
        </div>
    );
}
