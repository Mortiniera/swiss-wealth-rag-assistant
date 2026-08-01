import { useState, type FormEvent } from "react";
import { Button } from "../ui";

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
    <form
      className="flex shrink-0 items-end gap-2 border-t border-border bg-surface-raised pt-3"
      onSubmit={handleSubmit}
    >
      <input
        type="text"
        className="min-w-0 flex-1 border border-border bg-surface px-3 py-2.5 text-[0.875rem] text-ink placeholder:text-ink-tertiary focus:border-accent focus:outline-none"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a policy question…"
        disabled={disabled}
        aria-label="Question"
      />
      <Button
        type="submit"
        className="shrink-0 px-3.5 py-2.5 text-[0.8125rem] font-semibold"
        disabled={disabled || !question.trim()}
      >
        {disabled ? "…" : "Send"}
      </Button>
    </form>
  );
}
