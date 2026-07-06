export function DeploymentBanner() {
    if (!import.meta.env.PROD) {
        return null;
    }

    return (
        <details className="deployment-banner">
            <summary className="deployment-banner__summary">Demo hosting notice</summary>
            <p>
                This app runs on free-tier hosting (Vercel frontend, Render API). After inactivity,
                the API sleeps and can take <strong>30–60 seconds</strong> to wake up. On the first
                request, the backend may also index documents, so your first question can take up to a
                minute. Later questions are much faster.
            </p>
        </details>
    );
}
