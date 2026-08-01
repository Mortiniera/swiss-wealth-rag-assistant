import { Badge, Button } from "../ui";
import { Footer } from "../shell/Footer";
import { ChatWindow } from "./ChatWindow";
import { cn } from "../../utils/cn";
import type { SelectedClientContext } from "../../utils/personaView";

type AssistantDockProps = {
  open: boolean;
  onClose: () => void;
  clientContext?: SelectedClientContext | null;
};

export function AssistantDock({
  open,
  onClose,
  clientContext = null,
}: AssistantDockProps) {
  return (
    <aside
      id="assistant-dock"
      className={cn(
        "absolute inset-y-0 right-0 z-20 flex h-full shrink-0 flex-col bg-surface-raised transition-[width,opacity] duration-300 ease-[cubic-bezier(0.22,1,0.36,1)] md:static",
        open
          ? "pointer-events-auto w-full max-w-md border-l border-border opacity-100 shadow-[-8px_0_24px_rgb(11_18_32_/_0.07)] md:max-w-none md:w-[24rem]"
          : "pointer-events-none w-0 overflow-hidden border-l border-transparent opacity-0",
      )}
      aria-hidden={!open}
      aria-label="Operations assistant"
    >
      <div className="flex shrink-0 items-center justify-between gap-3 border-b border-border px-4 py-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h2 className="text-[0.875rem] font-semibold text-brand">Assistant</h2>
            <Badge>Policy</Badge>
          </div>
          <p className="mt-0.5 text-[0.6875rem] text-ink-tertiary">
            Grounded answers · verify sources
          </p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          aria-label="Close assistant"
          tabIndex={open ? 0 : -1}
        >
          Close
        </Button>
      </div>

      {clientContext && (
        <div className="shrink-0 border-b border-border bg-accent-soft/50 px-4 py-2">
          <p className="m-0 text-[0.6875rem] font-semibold tracking-[0.04em] text-ink-tertiary uppercase">
            Client context
          </p>
          <p className="mt-0.5 mb-0 truncate text-[0.8125rem] text-ink">
            <span className="font-mono font-medium">{clientContext.code}</span>
            <span className="text-ink-tertiary"> · </span>
            {clientContext.name}
          </p>
        </div>
      )}

      <div className="flex min-h-0 flex-1 flex-col overflow-hidden px-3 pt-3 pb-2">
        <ChatWindow compact clientContext={clientContext} />
      </div>

      <div className="shrink-0 border-t border-border px-4 py-2">
        <Footer />
      </div>
    </aside>
  );
}
