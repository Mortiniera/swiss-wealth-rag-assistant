import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { cn } from "../../utils/cn";
import type { ColumnSort, SortDirection } from "../../utils/tableSort";
import { FilterIcon } from "./icons";

type ColumnHeaderProps = {
  label: string;
  sortKey?: string;
  sort?: ColumnSort | null;
  onSort?: (key: string) => void;
  filterValue?: string;
  filterOptions?: { value: string; label: string }[];
  onFilter?: (value: string) => void;
};

function SortGlyph({ direction }: { direction: SortDirection | null }) {
  return (
    <span className="inline-flex flex-col leading-none" aria-hidden="true">
      <span
        className={cn(
          "text-[0.55rem]",
          direction === "asc" ? "text-brand" : "text-ink-tertiary/50",
        )}
      >
        ▲
      </span>
      <span
        className={cn(
          "-mt-0.5 text-[0.55rem]",
          direction === "desc" ? "text-brand" : "text-ink-tertiary/50",
        )}
      >
        ▼
      </span>
    </span>
  );
}

/** Column title with optional asc/desc sort and unique-value filter menu. */
export function ColumnHeader({
  label,
  sortKey,
  sort = null,
  onSort,
  filterValue = "all",
  filterOptions,
  onFilter,
}: ColumnHeaderProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const menuId = useId();
  const activeDir = sortKey && sort?.key === sortKey ? sort.direction : null;
  const filterActive = Boolean(filterOptions && filterValue !== "all");
  const canSort = Boolean(sortKey && onSort);
  const canFilter = Boolean(filterOptions && onFilter && filterOptions.length > 0);

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
    <div ref={rootRef} className="relative flex min-w-0 items-center gap-1">
      {canSort ? (
        <button
          type="button"
          className={cn(
            "inline-flex min-w-0 items-center gap-1 rounded-sm text-left text-[0.6875rem] font-semibold tracking-[0.04em] uppercase transition-colors",
            activeDir ? "text-brand" : "text-ink-tertiary hover:text-ink",
          )}
          onClick={() => onSort?.(sortKey!)}
          aria-label={`Sort by ${label}${activeDir ? `, currently ${activeDir}` : ""}`}
        >
          <span className="truncate">{label}</span>
          <SortGlyph direction={activeDir} />
        </button>
      ) : (
        <p className="m-0 truncate text-[0.6875rem] font-semibold tracking-[0.04em] text-ink-tertiary uppercase">
          {label}
        </p>
      )}

      {canFilter && (
        <>
          <button
            type="button"
            className={cn(
              "inline-flex size-5 shrink-0 items-center justify-center rounded-sm transition-colors",
              filterActive || open
                ? "bg-accent-soft text-brand"
                : "text-ink-tertiary/80 hover:bg-surface-raised hover:text-ink",
            )}
            aria-haspopup="listbox"
            aria-expanded={open}
            aria-controls={menuId}
            aria-label={`Filter ${label}`}
            onClick={() => setOpen((value) => !value)}
          >
            <FilterIcon active={filterActive} />
          </button>
          {open && (
            <ul
              id={menuId}
              role="listbox"
              aria-label={`${label} filter`}
              className="absolute top-full left-0 z-30 mt-1 max-h-56 min-w-[10rem] overflow-y-auto border border-border bg-surface-raised py-1 shadow-[0_8px_24px_rgb(11_18_32_/_0.12)]"
            >
              {filterOptions!.map((option) => (
                <li key={option.value} role="option" aria-selected={filterValue === option.value}>
                  <button
                    type="button"
                    className={cn(
                      "block w-full px-2.5 py-1.5 text-left text-[0.75rem] transition-colors",
                      filterValue === option.value
                        ? "bg-accent-soft font-medium text-brand"
                        : "text-ink hover:bg-surface-muted",
                    )}
                    onClick={() => {
                      onFilter?.(option.value);
                      setOpen(false);
                    }}
                  >
                    {option.label}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}

type DataTableProps = {
  headers: ReactNode;
  children: ReactNode;
  fill?: boolean;
  columnTemplate?: string;
  columnCount: number;
};

/** Directory table with custom interactive headers. */
export function DataTable({
  headers,
  children,
  fill = false,
  columnTemplate,
  columnCount,
}: DataTableProps) {
  const template =
    columnTemplate ?? `repeat(${columnCount}, minmax(0, 1fr))`;

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
        style={{ gridTemplateColumns: template }}
      >
        {headers}
      </div>
      {children}
    </div>
  );
}
