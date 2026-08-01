export function DeploymentBanner() {
    if (!import.meta.env.PROD) {
        return null;
    }

    return (
        <details className="deployment-banner">
            <summary className="deployment-banner__summary">Demo hosting notice</summary>
            <p>
                This demo runs on free-tier hosting: <strong>Vercel</strong> (UI),{" "}
                <strong>Render</strong> (API), and <strong>Neon</strong> (Postgres + pgvector).
                After inactivity the API sleeps and can take <strong>30–60 seconds</strong> to wake
                up. The first question after a cold start may be slow; later ones are much faster.
                Policy knowledge persists in Neon — it is not re-indexed on every wake.
            </p>
        </details>
    );
}
