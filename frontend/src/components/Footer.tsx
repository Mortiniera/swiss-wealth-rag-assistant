export function Footer() {
    return (
        <footer className="app__footer">
            <p>
                Author:{" "}
                <a href="https://github.com/MORTINIERA" target="_blank" rel="noopener noreferrer">
                    Mortiniera Thevie
                </a>
            </p>
            <p className="app__footer-links">
                <a href="https://github.com/MORTINIERA" target="_blank" rel="noopener noreferrer">
                    GitHub
                </a>
                <span aria-hidden="true"> · </span>
                <a
                    href="https://www.linkedin.com/in/thevie-mortiniera/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    LinkedIn
                </a>
                <span aria-hidden="true"> · </span>
                <span>2026</span>
            </p>
        </footer>
    );
}