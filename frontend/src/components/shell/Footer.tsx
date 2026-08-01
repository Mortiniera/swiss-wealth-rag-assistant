export function Footer() {
  return (
    <footer className="text-[0.6875rem] leading-snug text-ink-tertiary">
      <p className="m-0">
        Built by{" "}
        <a
          href="https://github.com/MORTINIERA"
          target="_blank"
          rel="noopener noreferrer"
          className="text-ink-secondary hover:text-brand hover:underline"
        >
          Thevie Mortiniera
        </a>
        <span aria-hidden="true"> · </span>
        <a
          href="https://github.com/MORTINIERA"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-brand hover:underline"
        >
          GitHub
        </a>
        <span aria-hidden="true"> · </span>
        <a
          href="https://www.linkedin.com/in/thevie-mortiniera/"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-brand hover:underline"
        >
          LinkedIn
        </a>
      </p>
    </footer>
  );
}
