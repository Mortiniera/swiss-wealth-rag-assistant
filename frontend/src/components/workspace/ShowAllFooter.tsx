import type { ReactNode } from "react";
import { Button } from "../ui";

type ShowAllFooterProps = {
  remaining: number;
  noun: string;
  onShowAll: () => void;
};

/** Footer CTA when a panel list is truncated to a short preview. */
export function ShowAllFooter({ remaining, noun, onShowAll }: ShowAllFooterProps) {
  if (remaining <= 0) return null;

  return (
    <div className="border-t border-border px-4 py-2.5">
      <Button variant="ghost" size="sm" className="w-full justify-center" onClick={onShowAll}>
        Show all · {remaining} more {noun}
        {remaining === 1 ? "" : "s"}
      </Button>
    </div>
  );
}

type EmptyPanelBodyProps = {
  children: ReactNode;
};

export function EmptyPanelBody({ children }: EmptyPanelBodyProps) {
  return <p className="m-0 px-4 py-6 text-[0.875rem] text-ink-secondary">{children}</p>;
}
