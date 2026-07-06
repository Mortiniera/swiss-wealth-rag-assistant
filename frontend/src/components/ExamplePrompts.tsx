const EXAMPLE_PROMPTS = [
    "Compare UBS and Pictet on wealth management positioning",
    "Summarize sustainable investing in Swiss banking",
    "How Governance is conducted within wealth management?",
    "Which sources mention private assets?",
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
