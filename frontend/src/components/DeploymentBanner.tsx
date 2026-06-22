export function DeploymentBanner() {
    if (!import.meta.env.PROD) {
        return null;
    }

    return (
        <aside className="deployment-banner" role="status">
            <p className="deployment-banner__title">Demo hosting notice</p>
            <p>
                This app runs on free-tier hosting (Vercel frontend, Render API). After
                inactivity, the API sleeps and can take <strong>30–60 seconds</strong> to
                wake up. On the first request, the backend may also index documents, so
                your first question can take up to a minute. Later questions are much
                faster.
            </p>
        </aside>
    );
}
