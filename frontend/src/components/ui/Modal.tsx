import { useEffect, useId, useRef, type ReactNode } from "react";
import { Button } from "./Button";

type ModalProps = {
  open: boolean;
  onClose: () => void;
  title: string;
  subtitle?: string;
  children: ReactNode;
  wide?: boolean;
};

export function Modal({ open, onClose, title, subtitle, children, wide = false }: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (open && !dialog.open) {
      dialog.showModal();
    } else if (!open && dialog.open) {
      dialog.close();
    }
  }, [open]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby={titleId}
      className={`m-auto max-h-[min(42rem,calc(100vh-3.5rem))] border border-border bg-surface-raised p-0 text-ink shadow-[0_16px_48px_rgb(11_18_32_/_0.18)] open:flex open:flex-col backdrop:bg-brand-deep/35 ${wide ? "w-[min(48rem,calc(100vw-2rem))]" : "w-[min(36rem,calc(100vw-2rem))]"}`}
      onClose={onClose}
      onClick={(event) => {
        if (event.target === dialogRef.current) onClose();
      }}
    >
      <header className="flex shrink-0 items-start justify-between gap-3 border-b border-border px-4 py-3">
        <div className="min-w-0">
          <h2 id={titleId} className="m-0 text-[0.9375rem] font-semibold text-brand">
            {title}
          </h2>
          {subtitle && (
            <p className="mt-0.5 mb-0 font-mono text-[0.75rem] text-ink-tertiary">{subtitle}</p>
          )}
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} aria-label="Close dialog">
          Close
        </Button>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-3">{children}</div>
    </dialog>
  );
}
