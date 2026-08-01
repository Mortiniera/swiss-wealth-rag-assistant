const EXAMPLE_PROMPTS = [
  "What does KYC refresh require when an ID expires?",
  "Why might an outbound transfer stay in pending review?",
  "What should an RM do about fragmented transfers?",
  "Which account restrictions exist, and who can lift them?",
] as const;

type ExamplePromptsProps = {
  onSelect: (prompt: string) => void;
  disabled?: boolean;
};

export function ExamplePrompts({ onSelect, disabled = false }: ExamplePromptsProps) {
  return (
    <div className="px-2 py-3">
      <p className="mb-2 text-[0.75rem] font-semibold tracking-[0.04em] text-ink-tertiary uppercase">
        Try asking
      </p>
      <ul className="m-0 flex list-none flex-col gap-px p-0">
        {EXAMPLE_PROMPTS.map((prompt) => (
          <li key={prompt}>
            <button
              type="button"
              className="w-full border-b border-border/80 px-1 py-2.5 text-left text-[0.8125rem] leading-snug text-ink transition-colors hover:bg-surface-raised hover:text-brand disabled:opacity-50"
              onClick={() => onSelect(prompt)}
              disabled={disabled}
            >
              {prompt}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
