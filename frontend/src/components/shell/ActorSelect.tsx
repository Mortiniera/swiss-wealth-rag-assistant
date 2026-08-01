import { useEffect, useId, useRef, useState } from "react";
import type { Actor } from "../../api/client";
import { cn } from "../../utils/cn";

type ActorSelectProps = {
  actors: Actor[];
  value: string | null;
  onChange: (employeeCode: string) => void;
  disabled?: boolean;
};

function ChevronDownIcon({ open }: { open: boolean }) {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      aria-hidden="true"
      className={cn("shrink-0 transition-transform", open && "rotate-180")}
    >
      <path
        d="M2.5 4.25 6 7.75l3.5-3.5"
        stroke="currentColor"
        strokeWidth="1.35"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/** Demo identity picker — custom menu opens downward (not native select). */
export function ActorSelect({
  actors,
  value,
  onChange,
  disabled = false,
}: ActorSelectProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const listId = useId();
  const selected = actors.find((actor) => actor.employee_code === value) ?? null;

  const grouped = new Map<string, Actor[]>();
  for (const actor of actors) {
    const bucket = grouped.get(actor.role_name) ?? [];
    bucket.push(actor);
    grouped.set(actor.role_name, bucket);
  }

  useEffect(() => {
    if (!open) return;

    function onPointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    }

    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }

    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div ref={rootRef} className="relative">
      <label className="flex items-center gap-2">
        <span className="hidden text-[0.75rem] font-medium text-ink-tertiary sm:inline">
          Act as
        </span>
        <button
          type="button"
          disabled={disabled || actors.length === 0}
          aria-haspopup="listbox"
          aria-expanded={open}
          aria-controls={listId}
          aria-label="Act as demo employee"
          onClick={() => setOpen((prev) => !prev)}
          className={cn(
            "inline-flex max-w-[14rem] items-center gap-2 rounded-sm border border-border bg-surface-raised py-1.5 pr-2 pl-2.5 text-left text-[0.8125rem] text-ink transition-colors",
            "hover:border-border-strong disabled:cursor-not-allowed disabled:opacity-60",
            open && "border-border-strong",
          )}
        >
          <span className="min-w-0 truncate">
            {selected ? selected.full_name : "Select employee"}
          </span>
          <ChevronDownIcon open={open} />
        </button>
      </label>

      {open && (
        <div
          id={listId}
          role="listbox"
          aria-label="Demo employees"
          className="absolute top-full right-0 z-40 mt-1 max-h-72 w-[min(20rem,calc(100vw-2rem))] overflow-y-auto border border-border bg-surface-raised py-1 shadow-[0_8px_24px_rgb(11_18_32_/_0.12)]"
        >
          {[...grouped.entries()].map(([roleName, rows]) => (
            <div key={roleName} role="group" aria-label={roleName}>
              <p className="m-0 px-2.5 pt-2 pb-1 text-[0.625rem] font-semibold tracking-[0.06em] text-ink-tertiary uppercase">
                {roleName}
              </p>
              {rows.map((actor) => {
                const isSelected = actor.employee_code === value;
                return (
                  <button
                    key={actor.employee_code}
                    type="button"
                    role="option"
                    aria-selected={isSelected}
                    className={cn(
                      "flex w-full flex-col gap-0.5 px-2.5 py-1.5 text-left transition-colors",
                      isSelected
                        ? "bg-accent-soft text-brand"
                        : "text-ink hover:bg-surface-muted",
                    )}
                    onClick={() => {
                      onChange(actor.employee_code);
                      setOpen(false);
                    }}
                  >
                    <span className="text-[0.8125rem] font-medium">
                      {actor.full_name}
                    </span>
                    <span className="font-mono text-[0.6875rem] text-ink-tertiary">
                      {actor.employee_code}
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
