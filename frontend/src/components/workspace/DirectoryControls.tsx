import { cn } from "../../utils/cn";

export type SegmentOption<T extends string> = {
  id: T;
  label: string;
  count?: number;
};

type SegmentedControlProps<T extends string> = {
  value: T;
  options: SegmentOption<T>[];
  onChange: (next: T) => void;
  "aria-label": string;
};

/** Compact toggle group for directory scope (All / Scenarios). */
export function SegmentedControl<T extends string>({
  value,
  options,
  onChange,
  "aria-label": ariaLabel,
}: SegmentedControlProps<T>) {
  return (
    <div
      className="inline-flex rounded-sm border border-border bg-surface-raised p-0.5"
      role="group"
      aria-label={ariaLabel}
    >
      {options.map((option) => (
        <button
          key={option.id}
          type="button"
          onClick={() => onChange(option.id)}
          className={cn(
            "rounded-sm px-2.5 py-1 text-[0.75rem] font-medium transition-colors",
            value === option.id
              ? "bg-brand text-white"
              : "text-ink-secondary hover:bg-surface-muted hover:text-ink",
          )}
          aria-pressed={value === option.id}
        >
          {option.label}
          {option.count != null && (
            <span className="ml-1 tabular-nums opacity-80">{option.count}</span>
          )}
        </button>
      ))}
    </div>
  );
}
