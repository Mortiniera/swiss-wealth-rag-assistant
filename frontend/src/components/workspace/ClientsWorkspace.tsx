import { useEffect } from "react";
import { useClientDetail } from "../../hooks/useClientDetail";
import { useClients, type ClientListFilter } from "../../hooks/useClients";
import type { WorkspaceContext } from "../../api/client";
import type { SelectedClientContext } from "../../utils/personaView";
import { ChevronLeftIcon, SearchField } from "../ui";
import { ClientDetailPanels } from "./ClientDetailPanels";
import { ClientDirectory } from "./ClientDirectory";
import { SegmentedControl } from "./DirectoryControls";
import { PageHeader } from "./PageHeader";
import { PaginationBar } from "./PaginationBar";

type ClientsWorkspaceProps = {
  workspace: WorkspaceContext;
  selectedClient: SelectedClientContext | null;
  onSelectedClientChange: (client: SelectedClientContext | null) => void;
};

export function ClientsWorkspace({
  workspace,
  selectedClient,
  onSelectedClientChange,
}: ClientsWorkspaceProps) {
  const {
    clients,
    matchedCount,
    totalCount,
    scenarioCount,
    filterOptions,
    columnFilters,
    setColumnFilter,
    sort,
    toggleSort,
    loading,
    error,
    query,
    setQuery,
    listFilter,
    setListFilter,
    page,
    setPage,
    pageCount,
    rangeStart,
    rangeEnd,
  } = useClients(workspace.actor.employee_code);

  const selectedCode = selectedClient?.code ?? null;
  const detail = useClientDetail(selectedCode);
  const inDetail = selectedCode !== null;

  // Only refresh the display name once a client is already selected.
  // Never re-assert selection when the user cleared it (Back) — that race
  // used to fight handleBack while detail.client was still briefly populated.
  useEffect(() => {
    if (!selectedClient || !detail.client) return;
    if (selectedClient.code !== detail.client.client_code) return;
    if (selectedClient.name === detail.client.full_name) return;
    onSelectedClientChange({
      code: detail.client.client_code,
      name: detail.client.full_name,
    });
  }, [detail.client, selectedClient, onSelectedClientChange]);

  function handleBack() {
    onSelectedClientChange(null);
  }

  function handlePageChange(next: number) {
    setPage(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (inDetail) {
    const title = detail.client?.full_name ?? selectedClient?.name ?? selectedCode;
    const code = detail.client?.client_code ?? selectedCode;

    return (
      <div className="flex min-h-0 flex-1 flex-col gap-4 animate-[canvas-fade_280ms_ease-out_both]">
        <PageHeader
          breadcrumb={
            <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-[0.75rem]">
              <button
                type="button"
                onClick={handleBack}
                className="inline-flex items-center gap-0.5 font-medium text-accent hover:underline"
              >
                <ChevronLeftIcon />
                Clients
              </button>
              <span className="text-ink-tertiary" aria-hidden="true">
                /
              </span>
              <span className="font-mono text-ink-secondary">{code}</span>
            </nav>
          }
          title={title ?? "Client"}
          description={
            detail.client
              ? `${detail.client.client_code} · ${detail.client.primary_assignment?.full_name ?? "Unassigned"} · ${detail.client.residency_country}`
              : "Loading client record…"
          }
        />

        {detail.loading && (
          <p className="text-[0.875rem] text-ink-secondary">Loading client detail…</p>
        )}
        {detail.error && <p className="text-[0.875rem] text-danger">{detail.error}</p>}

        {detail.client && !detail.loading && (
          <ClientDetailPanels
            layout={workspace.panel_layout}
            client={detail.client}
            accounts={detail.accounts}
            transactions={detail.transactions}
            serviceRequests={detail.serviceRequests}
            interactions={detail.interactions}
          />
        )}
      </div>
    );
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      <PageHeader
        title="Clients"
        description={
          workspace.client_scope === "assigned"
            ? "Assigned client book for this demo identity."
            : "Full client book for this role."
        }
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {scenarioCount > 0 ? (
              <SegmentedControl<ClientListFilter>
                aria-label="Client book scope"
                value={listFilter}
                onChange={setListFilter}
                options={[
                  { id: "all", label: "All", count: totalCount },
                  { id: "scenarios", label: "Scenarios", count: scenarioCount },
                ]}
              />
            ) : (
              <p className="m-0 text-[0.75rem] tabular-nums text-ink-tertiary">
                {totalCount} clients
              </p>
            )}
            <SearchField
              placeholder="Search clients"
              aria-label="Search clients"
              value={query}
              onChange={setQuery}
            />
          </div>
        }
      />

      <ClientDirectory
        clients={clients}
        loading={loading}
        error={error}
        showRmColumn={workspace.client_scope !== "assigned"}
        onSelect={(clientCode) => {
          const row = clients.find((client) => client.client_code === clientCode);
          onSelectedClientChange({
            code: clientCode,
            name: row?.full_name ?? clientCode,
          });
        }}
        sort={sort}
        onSort={toggleSort}
        columnFilters={columnFilters}
        filterOptions={filterOptions}
        onColumnFilter={setColumnFilter}
      />

      {!loading && !error && (
        <PaginationBar
          page={page}
          pageCount={pageCount}
          rangeStart={rangeStart}
          rangeEnd={rangeEnd}
          total={matchedCount}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  );
}
