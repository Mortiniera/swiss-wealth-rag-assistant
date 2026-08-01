import type { ReactNode } from "react";

type DataTableProps = {
  columns: readonly string[];
  children: ReactNode;
  /** When true, table grows to fill leftover workspace height. */
  fill?: boolean;
};

/** Lightweight table chrome (header + body region) for directory/catalog views. */
export function DataTable({ columns, children, fill = false }: DataTableProps) {
  return (
    <div
      className={
        fill
          ? "flex min-h-0 flex-1 flex-col overflow-hidden border border-border bg-surface-raised"
          : "border border-border bg-surface-raised"
      }
    >
      <div
        className="sticky top-0 z-10 grid gap-3 border-b border-border bg-surface-muted px-4 py-2.5 shadow-[0_1px_0_rgb(215_221_230)]"
        style={{ gridTemplateColumns: `repeat(${columns.length}, minmax(0, 1fr))` }}
      >
        {columns.map((column) => (
          <p
            key={column}
            className="m-0 text-[0.6875rem] font-semibold tracking-[0.04em] text-ink-tertiary uppercase"
          >
            {column}
          </p>
        ))}
      </div>
      {children}
    </div>
  );
}
