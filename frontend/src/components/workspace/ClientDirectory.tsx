import type { Client } from "../../api/client";
import {
  clientOpenItems,
  formatLabel,
} from "../../utils/clientDisplay";
import type { ColumnSort } from "../../utils/tableSort";
import { Badge, ColumnHeader, DataTable, EmptyState } from "../ui";
import type { ClientColumnFilters } from "../../hooks/useClients";

const COLUMN_TEMPLATE_FULL =
  "minmax(0,1.5fr) minmax(0,0.95fr) minmax(0,1.25fr) minmax(0,0.9fr) minmax(0,1fr)";

const COLUMN_TEMPLATE_NO_RM =
  "minmax(0,1.6fr) minmax(0,1fr) minmax(0,0.9fr) minmax(0,1.1fr)";

type ClientDirectoryProps = {
  clients: Client[];
  loading: boolean;
  error: string | null;
  onSelect: (clientCode: string) => void;
  sort: ColumnSort | null;
  onSort: (key: string) => void;
  columnFilters: ClientColumnFilters;
  filterOptions: {
    rm: string[];
    risk: string[];
    openItem: string[];
  };
  onColumnFilter: <K extends keyof ClientColumnFilters>(
    key: K,
    value: ClientColumnFilters[K],
  ) => void;
  /** Hide RM column when the book is already assigned-scoped. */
  showRmColumn?: boolean;
};

function withAll(options: string[], format: (value: string) => string = (v) => v) {
  return [
    { value: "all", label: "All" },
    ...options.map((value) => ({ value, label: format(value) })),
  ];
}

export function ClientDirectory({
  clients,
  loading,
  error,
  onSelect,
  sort,
  onSort,
  columnFilters,
  filterOptions,
  onColumnFilter,
  showRmColumn = true,
}: ClientDirectoryProps) {
  const columnTemplate = showRmColumn ? COLUMN_TEMPLATE_FULL : COLUMN_TEMPLATE_NO_RM;
  const columnCount = showRmColumn ? 5 : 4;

  return (
    <DataTable
      columnCount={columnCount}
      columnTemplate={columnTemplate}
      headers={
        <>
          <ColumnHeader label="Client" sortKey="name" sort={sort} onSort={onSort} />
          <ColumnHeader label="Code" sortKey="code" sort={sort} onSort={onSort} />
          {showRmColumn && (
            <ColumnHeader
              label="Relationship manager"
              sortKey="rm"
              sort={sort}
              onSort={onSort}
              filterValue={columnFilters.rm}
              filterOptions={withAll(filterOptions.rm)}
              onFilter={(value) => onColumnFilter("rm", value)}
            />
          )}
          <ColumnHeader
            label="Risk"
            sortKey="risk"
            sort={sort}
            onSort={onSort}
            filterValue={columnFilters.risk}
            filterOptions={withAll(filterOptions.risk, formatLabel)}
            onFilter={(value) => onColumnFilter("risk", value)}
          />
          <ColumnHeader
            label="Open items"
            sortKey="openItem"
            sort={sort}
            onSort={onSort}
            filterValue={columnFilters.openItem}
            filterOptions={withAll(filterOptions.openItem)}
            onFilter={(value) => onColumnFilter("openItem", value)}
          />
        </>
      }
    >
      {loading && (
        <p className="px-4 py-6 text-[0.875rem] text-ink-secondary">Loading clients…</p>
      )}

      {!loading && error && (
        <p className="px-4 py-6 text-[0.875rem] text-danger">{error}</p>
      )}

      {!loading && !error && clients.length === 0 && (
        <EmptyState
          title="No clients found"
          description="No clients match the current filters."
        />
      )}

      {!loading && !error && clients.length > 0 && (
        <ul className="m-0 list-none p-0">
          {clients.map((client) => {
            const openItem = clientOpenItems(client);
            return (
              <li key={client.id} className="m-0 border-b border-border last:border-b-0">
                <button
                  type="button"
                  onClick={() => onSelect(client.client_code)}
                  className="grid w-full gap-3 px-4 py-3 text-left transition-colors hover:bg-surface-muted/70"
                  style={{ gridTemplateColumns: columnTemplate }}
                >
                  <span className="min-w-0 truncate self-center text-[0.8125rem] font-semibold text-ink">
                    {client.full_name}
                  </span>
                  <span className="truncate self-center font-mono text-[0.75rem] text-ink-tertiary">
                    {client.client_code}
                  </span>
                  {showRmColumn && (
                    <span className="truncate self-center text-[0.8125rem] text-ink-secondary">
                      {client.primary_assignment?.full_name ?? "—"}
                    </span>
                  )}
                  <span className="truncate self-center text-[0.8125rem] capitalize text-ink-secondary">
                    {formatLabel(client.suitability_profile?.risk_profile)}
                  </span>
                  <span className="flex items-center self-center">
                    {openItem === "—" ? (
                      <span className="text-[0.8125rem] text-ink-tertiary">—</span>
                    ) : (
                      <Badge tone="warning">{openItem}</Badge>
                    )}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </DataTable>
  );
}
