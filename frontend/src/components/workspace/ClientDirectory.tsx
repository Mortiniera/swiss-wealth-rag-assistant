import type { Client } from "../../api/client";
import { clientOpenItems, formatLabel } from "../../utils/clientDisplay";
import { Badge, DataTable, EmptyState } from "../ui";

const COLUMNS = ["Client", "Relationship manager", "Risk", "Open items"] as const;

type ClientDirectoryProps = {
  clients: Client[];
  loading: boolean;
  error: string | null;
  onSelect: (clientCode: string) => void;
};

export function ClientDirectory({
  clients,
  loading,
  error,
  onSelect,
}: ClientDirectoryProps) {
  return (
    <DataTable columns={COLUMNS}>
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
                  className="grid w-full grid-cols-4 gap-3 px-4 py-3 text-left transition-colors hover:bg-surface-muted/70"
                >
                  <span className="min-w-0">
                    <span className="block truncate text-[0.8125rem] font-semibold text-ink">
                      {client.full_name}
                    </span>
                    <span className="mt-0.5 block font-mono text-[0.6875rem] text-ink-tertiary">
                      {client.client_code}
                    </span>
                  </span>
                  <span className="truncate self-center text-[0.8125rem] text-ink-secondary">
                    {client.primary_assignment?.full_name ?? "—"}
                  </span>
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
