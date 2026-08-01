import { AskIcon, Button } from "../ui";
import { PersonaSelect } from "./PersonaSelect";
import type { PersonaId } from "../../types/workspace";

type TopBarProps = {
  persona: PersonaId;
  onPersonaChange: (persona: PersonaId) => void;
  dockOpen: boolean;
  onToggleDock: () => void;
};

export function TopBar({
  persona,
  onPersonaChange,
  dockOpen,
  onToggleDock,
}: TopBarProps) {
  return (
    <header className="relative flex h-14 shrink-0 items-center justify-between gap-4 border-b border-border bg-surface-raised px-4 sm:pl-16">
      <div
        className="pointer-events-none absolute inset-y-0 left-0 w-[3px] bg-brand"
        aria-hidden="true"
      />

      <div className="flex min-w-0 items-center gap-3">
        <div className="min-w-0">
          <p className="font-serif text-[1.0625rem] leading-none font-semibold tracking-[-0.02em] text-brand">
            Helvetia Private Bank
          </p>
          <p className="mt-1 text-[0.6875rem] font-medium tracking-[0.04em] text-ink-tertiary">
            Internal operations workspace
          </p>
        </div>
        <span className="hidden h-7 w-px bg-border sm:block" aria-hidden="true" />
        <h1 className="hidden text-[0.8125rem] font-semibold tracking-[0.08em] text-ink-secondary uppercase sm:block">
          Operations
        </h1>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <PersonaSelect value={persona} onChange={onPersonaChange} />
        <Button
          variant={dockOpen ? "soft" : "primary"}
          onClick={onToggleDock}
          aria-pressed={dockOpen}
          aria-controls="assistant-dock"
        >
          <AskIcon />
          {dockOpen ? "Hide assistant" : "Ask"}
        </Button>
      </div>
    </header>
  );
}
