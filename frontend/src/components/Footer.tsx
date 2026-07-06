export function Footer() {
    return (
        <footer className="app__footer">
            <p>
                Built by{" "}
                <a href="https://github.com/MORTINIERA" target="_blank" rel="noopener noreferrer">
                    Thevie Mortiniera
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
            </p>
        </footer>
    );
}
