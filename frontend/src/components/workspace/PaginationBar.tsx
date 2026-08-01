import { Button, ChevronLeftIcon, ChevronRightIcon } from "../ui";

type PaginationBarProps = {
  page: number;
  pageCount: number;
  rangeStart: number;
  rangeEnd: number;
  total: number;
  onPageChange: (page: number) => void;
  noun?: string;
};

/** Compact Previous / Next pager for dense ops tables. */
export function PaginationBar({
  page,
  pageCount,
  rangeStart,
  rangeEnd,
  total,
  onPageChange,
  noun = "client",
}: PaginationBarProps) {
  if (total === 0) return null;

  const plural = total === 1 ? noun : `${noun}s`;

  return (
    <div
      className="flex flex-wrap items-center justify-between gap-3 border border-border bg-surface-raised px-4 py-2.5"
      role="navigation"
      aria-label="Pagination"
    >
      <p className="m-0 text-[0.8125rem] text-ink-secondary">
        <span className="tabular-nums text-ink">
          {rangeStart}–{rangeEnd}
        </span>
        {" of "}
        <span className="tabular-nums">{total}</span> {plural}
      </p>

      <div className="flex items-center gap-2">
        <p className="m-0 text-[0.75rem] text-ink-tertiary">
          Page <span className="tabular-nums text-ink">{page}</span> of{" "}
          <span className="tabular-nums text-ink">{pageCount}</span>
        </p>
        <Button
          variant="outline"
          size="sm"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          aria-label="Previous page"
        >
          <ChevronLeftIcon />
          Prev
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= pageCount}
          onClick={() => onPageChange(page + 1)}
          aria-label="Next page"
        >
          Next
          <ChevronRightIcon />
        </Button>
      </div>
    </div>
  );
}
