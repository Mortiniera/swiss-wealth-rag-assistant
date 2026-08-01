import { useState, type ReactNode } from "react";
import type {
  Account,
  Client,
  ClientPanelId,
  Interaction,
  PanelLayout,
  ServiceRequest,
  Transaction,
} from "../../api/client";
import { ClientAccountsPanel } from "./ClientAccountsPanel";
import { ClientInteractionsPanel } from "./ClientInteractionsPanel";
import { ClientProfilePanel } from "./ClientProfilePanel";
import { ClientServiceRequestsPanel } from "./ClientServiceRequestsPanel";
import { ClientTransactionsPanel } from "./ClientTransactionsPanel";

type ClientDetailPanelsProps = {
  layout: PanelLayout;
  client: Client;
  accounts: Account[];
  transactions: Transaction[];
  serviceRequests: ServiceRequest[];
  interactions: Interaction[];
};

function renderPanel(
  id: ClientPanelId,
  props: Omit<ClientDetailPanelsProps, "layout">,
): ReactNode {
  switch (id) {
    case "profile":
      return <ClientProfilePanel key={id} client={props.client} />;
    case "accounts":
      return <ClientAccountsPanel key={id} accounts={props.accounts} />;
    case "transactions":
      return <ClientTransactionsPanel key={id} transactions={props.transactions} />;
    case "service_requests":
      return <ClientServiceRequestsPanel key={id} requests={props.serviceRequests} />;
    case "interactions":
      return <ClientInteractionsPanel key={id} interactions={props.interactions} />;
    default:
      return null;
  }
}

function layoutPanels(
  ids: ClientPanelId[],
  props: Omit<ClientDetailPanelsProps, "layout">,
): ReactNode[] {
  const nodes: ReactNode[] = [];
  let index = 0;
  while (index < ids.length) {
    const current = ids[index];
    const next = ids[index + 1];
    const pairProfile = current === "profile" && next === "accounts";
    const pairService =
      current === "service_requests" && next === "interactions";

    if (pairProfile || pairService) {
      nodes.push(
        <div key={`${current}-${next}`} className="grid gap-4 lg:grid-cols-2">
          {renderPanel(current, props)}
          {renderPanel(next, props)}
        </div>,
      );
      index += 2;
      continue;
    }

    nodes.push(renderPanel(current, props));
    index += 1;
  }
  return nodes;
}

export function ClientDetailPanels({
  layout,
  client,
  accounts,
  transactions,
  serviceRequests,
  interactions,
}: ClientDetailPanelsProps) {
  const [showSecondary, setShowSecondary] = useState(false);
  const panelProps = { client, accounts, transactions, serviceRequests, interactions };

  return (
    <div className="flex flex-col gap-4">
      <p className="m-0 rounded-sm border border-border bg-accent-soft/60 px-3 py-2 text-[0.8125rem] text-ink-secondary">
        {layout.focus_hint}
      </p>

      {layoutPanels(layout.primary, panelProps)}

      {layout.secondary.length > 0 && (
        <div className="border border-dashed border-border bg-surface-raised/60 px-3 py-3">
          <button
            type="button"
            className="text-[0.8125rem] font-medium text-accent hover:underline"
            onClick={() => setShowSecondary((value) => !value)}
            aria-expanded={showSecondary}
          >
            {showSecondary
              ? "Hide secondary sections"
              : `Show ${layout.secondary.length} secondary section${layout.secondary.length === 1 ? "" : "s"}`}
          </button>
          {showSecondary && (
            <div className="mt-3 flex flex-col gap-4 opacity-90">
              {layoutPanels(layout.secondary, panelProps)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
