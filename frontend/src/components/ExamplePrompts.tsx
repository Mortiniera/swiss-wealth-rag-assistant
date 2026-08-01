const EXAMPLE_PROMPTS = [
    "What does the KYC refresh policy require when an ID expires?",
    "Why might an outbound transfer stay in pending review?",
    "What should an RM do if they notice unusual fragmented transfers?",
    "What types of account restrictions exist and who can lift them?",
] as const;

type ExamplePromptsProps = {
    onSelect: (prompt: string) => void;
    disabled?: boolean;
};

export function ExamplePrompts({ onSelect, disabled = false }: ExamplePromptsProps) {
    return (
        <div className="example-prompts">
            <p className="example-prompts__label">Try an example question</p>
            <div className="example-prompts__grid">
                {EXAMPLE_PROMPTS.map((prompt) => (
                    <button
                        key={prompt}
                        type="button"
                        className="example-prompts__chip"
                        onClick={() => onSelect(prompt)}
                        disabled={disabled}
                    >
                        {prompt}
                    </button>
                ))}
            </div>
        </div>
    );
}
