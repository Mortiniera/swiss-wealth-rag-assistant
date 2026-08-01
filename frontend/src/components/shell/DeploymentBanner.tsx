export function DeploymentBanner() {
  if (!import.meta.env.PROD) {
    return null;
  }

  return (
    <details className="group mt-3 rounded-sm border border-border bg-surface-raised px-3 py-2 text-[0.75rem] leading-snug text-ink-secondary">
      <summary className="cursor-pointer list-none font-medium text-ink-secondary marker:content-none [&::-webkit-details-marker]:hidden before:mr-1 before:inline-block before:transition-transform before:content-['▸'] group-open:before:rotate-90">
        Demo hosting notice
      </summary>
      <p className="mt-1.5 mb-0">
        This demo runs on free-tier hosting: <strong>Vercel</strong> (UI),{" "}
        <strong>Render</strong> (API), and <strong>Neon</strong> (Postgres + pgvector).
        After inactivity the API sleeps and can take <strong>30–60 seconds</strong> to wake
        up. The first question after a cold start may be slow; later ones are much faster.
        Policy knowledge persists in Neon — it is not re-indexed on every wake.
      </p>
    </details>
  );
}
