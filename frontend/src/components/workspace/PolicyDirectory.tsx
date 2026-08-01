import type { PolicySummary } from "../../api/client";
import type { PolicyColumnFilters } from "../../hooks/usePolicies";
import { formatDate, formatLabel } from "../../utils/clientDisplay";
import type { ColumnSort } from "../../utils/tableSort";
import { ColumnHeader, DataTable, EmptyState } from "../ui";

const COLUMN_TEMPLATE =
  "minmax(0,2fr) minmax(0,1fr) minmax(0,1.1fr) minmax(0,0.9fr)";

type PolicyDirectoryProps = {
  policies: PolicySummary[];
  loading: boolean;
  error: string | null;
  onSelect: (documentId: string) => void;
  sort: ColumnSort | null;
  onSort: (key: string) => void;
  columnFilters: PolicyColumnFilters;
  filterOptions: {
    category: string[];
    department: string[];
  };
  onColumnFilter: <K extends keyof PolicyColumnFilters>(
    key: K,
    value: PolicyColumnFilters[K],
  ) => void;
};

function withAll(options: string[], format: (value: string) => string = (v) => v) {
  return [
    { value: "all", label: "All" },
    ...options.map((value) => ({ value, label: format(value) })),
  ];
}

export function PolicyDirectory({
  policies,
  loading,
  error,
  onSelect,
  sort,
  onSort,
  columnFilters,
  filterOptions,
  onColumnFilter,
}: PolicyDirectoryProps) {
  return (
    <DataTable
      columnCount={4}
      columnTemplate={COLUMN_TEMPLATE}
      headers={
        <>
          <ColumnHeader label="Document" sortKey="title" sort={sort} onSort={onSort} />
          <ColumnHeader
            label="Category"
            sortKey="category"
            sort={sort}
            onSort={onSort}
            filterValue={columnFilters.category}
            filterOptions={withAll(filterOptions.category, formatLabel)}
            onFilter={(value) => onColumnFilter("category", value)}
          />
          <ColumnHeader
            label="Department"
            sortKey="department"
            sort={sort}
            onSort={onSort}
            filterValue={columnFilters.department}
            filterOptions={withAll(filterOptions.department)}
            onFilter={(value) => onColumnFilter("department", value)}
          />
          <ColumnHeader
            label="Effective"
            sortKey="effective"
            sort={sort}
            onSort={onSort}
          />
        </>
      }
    >
      {loading && (
        <p className="px-4 py-6 text-[0.875rem] text-ink-secondary">Loading policies…</p>
      )}

      {!loading && error && (
        <p className="px-4 py-6 text-[0.875rem] text-danger">{error}</p>
      )}

      {!loading && !error && policies.length === 0 && (
        <EmptyState
          title="No policies found"
          description="No policies match the current filters."
        />
      )}

      {!loading && !error && policies.length > 0 && (
        <ul className="m-0 list-none p-0">
          {policies.map((policy) => (
            <li key={policy.id} className="m-0 border-b border-border last:border-b-0">
              <button
                type="button"
                onClick={() => onSelect(policy.document_id)}
                className="grid w-full gap-3 px-4 py-3 text-left transition-colors hover:bg-surface-muted/70"
                style={{ gridTemplateColumns: COLUMN_TEMPLATE }}
              >
                <span className="min-w-0">
                  <span className="block truncate text-[0.8125rem] font-semibold text-ink">
                    {policy.title}
                  </span>
                  <span className="mt-0.5 block font-mono text-[0.6875rem] text-ink-tertiary">
                    {policy.document_id} · v{policy.version}
                  </span>
                </span>
                <span className="truncate self-center text-[0.8125rem] text-ink-secondary">
                  {formatLabel(policy.category)}
                </span>
                <span className="truncate self-center text-[0.8125rem] text-ink-secondary">
                  {policy.department}
                </span>
                <span className="self-center text-[0.8125rem] tabular-nums text-ink-secondary">
                  {formatDate(policy.effective_date)}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </DataTable>
  );
}
