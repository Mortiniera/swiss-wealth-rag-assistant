import { SearchIcon } from "./icons";

type SearchFieldProps = {
  placeholder: string;
  "aria-label": string;
  disabled?: boolean;
  value?: string;
  onChange?: (value: string) => void;
  className?: string;
};

export function SearchField({
  placeholder,
  "aria-label": ariaLabel,
  disabled = false,
  value,
  onChange,
  className = "w-44 sm:w-52",
}: SearchFieldProps) {
  return (
    <div className={`relative ${className}`}>
      <span className="pointer-events-none absolute top-1/2 left-2.5 -translate-y-1/2 text-ink-tertiary">
        <SearchIcon />
      </span>
      <input
        type="search"
        disabled={disabled}
        placeholder={placeholder}
        aria-label={ariaLabel}
        value={value}
        onChange={onChange ? (event) => onChange(event.target.value) : undefined}
        className="w-full rounded-sm border border-border bg-surface-raised py-1.5 pr-2.5 pl-8 text-[0.8125rem] text-ink placeholder:text-ink-tertiary disabled:text-ink-tertiary"
      />
    </div>
  );
}
