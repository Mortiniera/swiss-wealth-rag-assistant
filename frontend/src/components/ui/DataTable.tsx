import type { ReactNode } from "react";

type DataTableProps = {
  columns: readonly string[];
  children: ReactNode;
};

/** Lightweight table chrome (header + body region) for directory/catalog views. */
export function DataTable({ columns, children }: DataTableProps) {
  return (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden border border-border bg-surface-raised">
      <div
        className="grid gap-3 border-b border-border bg-surface-muted/80 px-4 py-2.5"
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
