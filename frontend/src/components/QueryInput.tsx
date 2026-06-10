import { useState, type FormEvent } from "react";

type QueryInputProps = {
    onSubmit: (question: string) => void;
    disabled?: boolean;
};

export function QueryInput({ onSubmit, disabled = false }: QueryInputProps) {
    const [question, setQuestion] = useState("");

    function handleSubmit(event: FormEvent) {
        event.preventDefault();
        const trimmed = question.trim();
        if (!trimmed || disabled) return;
        onSubmit(trimmed);
        setQuestion("");
    }

    return (
        <form className="query-input" onSubmit={handleSubmit}>
            <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask about Swiss wealth management..."
                disabled={disabled}
                aria-label="Question"
            />
            <button type="submit" disabled={disabled || !question.trim()}>
                {disabled ? "Thinking..." : "Ask"}
            </button>
        </form>
    );
}