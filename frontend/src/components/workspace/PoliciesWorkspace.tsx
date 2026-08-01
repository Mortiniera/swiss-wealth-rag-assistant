import { useState } from "react";
import { usePolicies } from "../../hooks/usePolicies";
import { usePolicyDetail } from "../../hooks/usePolicyDetail";
import { formatDate, formatLabel } from "../../utils/clientDisplay";
import { ChevronLeftIcon, SearchField } from "../ui";
import { PageHeader } from "./PageHeader";
import { PaginationBar } from "./PaginationBar";
import { PolicyDetailPanel } from "./PolicyDetailPanel";
import { PolicyDirectory } from "./PolicyDirectory";

type PoliciesWorkspaceProps = {
  actorCode: string;
};

export function PoliciesWorkspace({ actorCode }: PoliciesWorkspaceProps) {
  const {
    policies,
    matchedCount,
    filterOptions,
    columnFilters,
    setColumnFilter,
    sort,
    toggleSort,
    loading,
    error,
    query,
    setQuery,
    page,
    setPage,
    pageCount,
    rangeStart,
    rangeEnd,
  } = usePolicies(actorCode);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const detail = usePolicyDetail(selectedId);
  const inDetail = selectedId !== null;

  function handleBack() {
    setSelectedId(null);
  }

  function handlePageChange(next: number) {
    setPage(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  if (inDetail) {
    const title = detail.policy?.title ?? selectedId;
    const code = detail.policy?.document_id ?? selectedId;

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
                Policies
              </button>
              <span className="text-ink-tertiary" aria-hidden="true">
                /
              </span>
              <span className="font-mono text-ink-secondary">{code}</span>
            </nav>
          }
          title={title ?? "Policy"}
          description={
            detail.policy
              ? `${formatLabel(detail.policy.category)} · ${detail.policy.department} · Effective ${formatDate(detail.policy.effective_date)}`
              : "Loading policy…"
          }
        />

        {detail.loading && (
          <p className="text-[0.875rem] text-ink-secondary">Loading policy detail…</p>
        )}
        {detail.error && <p className="text-[0.875rem] text-danger">{detail.error}</p>}

        {detail.policy && !detail.loading && <PolicyDetailPanel policy={detail.policy} />}
      </div>
    );
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      <PageHeader
        title="Policies"
        description="Active Helvetia policies for KYC, transfers, AML, and restrictions."
        actions={
          <SearchField
            placeholder="Search policies"
            aria-label="Search policies"
            value={query}
            onChange={setQuery}
          />
        }
      />

      <PolicyDirectory
        policies={policies}
        loading={loading}
        error={error}
        onSelect={setSelectedId}
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
          noun="policy"
        />
      )}
    </div>
  );
}
