import { useState } from "react";
import { useClientDetail } from "../../hooks/useClientDetail";
import { useClients, type ClientListFilter } from "../../hooks/useClients";
import { Button, ChevronLeftIcon, SearchField } from "../ui";
import { ClientAccountsPanel } from "./ClientAccountsPanel";
import { ClientDirectory } from "./ClientDirectory";
import { ClientInteractionsPanel } from "./ClientInteractionsPanel";
import { ClientProfilePanel } from "./ClientProfilePanel";
import { ClientServiceRequestsPanel } from "./ClientServiceRequestsPanel";
import { ClientTransactionsPanel } from "./ClientTransactionsPanel";
import { SegmentedControl } from "./DirectoryControls";
import { PageHeader } from "./PageHeader";
import { PaginationBar } from "./PaginationBar";

export function ClientsWorkspace() {
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
  } = useClients();
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const detail = useClientDetail(selectedCode);
  const inDetail = selectedCode !== null;

  function handleBack() {
    setSelectedCode(null);
  }

  function handlePageChange(next: number) {
    setPage(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (inDetail) {
    const title = detail.client?.full_name ?? selectedCode;
    const code = detail.client?.client_code ?? selectedCode;

    return (
      <div className="flex min-h-0 flex-1 flex-col gap-4 animate-[canvas-fade_280ms_ease-out_both]">
        <PageHeader
          breadcrumb={
            <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-[0.75rem]">
              <button
                type="button"
                onClick={handleBack}
                className="font-medium text-accent hover:underline"
              >
                Clients
              </button>
              <span className="text-ink-tertiary" aria-hidden="true">
                /
              </span>
              <span className="font-mono text-ink-secondary">{code}</span>
            </nav>
          }
          leading={
            <Button
              variant="outline"
              size="sm"
              className="mt-0.5 shrink-0"
              onClick={handleBack}
              aria-label="Back to client directory"
            >
              <ChevronLeftIcon />
              Back
            </Button>
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
          <div className="flex flex-col gap-4">
            <div className="grid gap-4 lg:grid-cols-2">
              <ClientProfilePanel client={detail.client} />
              <ClientAccountsPanel accounts={detail.accounts} />
            </div>
            <ClientTransactionsPanel transactions={detail.transactions} />
            <div className="grid gap-4 lg:grid-cols-2">
              <ClientServiceRequestsPanel requests={detail.serviceRequests} />
              <ClientInteractionsPanel interactions={detail.interactions} />
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      <PageHeader
        title="Clients"
        description="Client book for service, KYC, and transfer review."
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <SegmentedControl<ClientListFilter>
              aria-label="Client book scope"
              value={listFilter}
              onChange={setListFilter}
              options={[
                { id: "all", label: "All", count: totalCount },
                { id: "scenarios", label: "Scenarios", count: scenarioCount },
              ]}
            />
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
        onSelect={setSelectedCode}
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
