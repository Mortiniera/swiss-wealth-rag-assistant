import { useEffect, useMemo, useState } from "react";
import { ApiError, listPolicies, type PolicySummary } from "../api/client";
import {
  compareText,
  cycleSort,
  type ColumnSort,
} from "../utils/tableSort";

/** Rows per policies directory page. */
export const POLICY_PAGE_SIZE = 25;

export type PolicyColumnFilters = {
  category: string;
  department: string;
};

const DEFAULT_FILTERS: PolicyColumnFilters = {
  category: "all",
  department: "all",
};

function uniqueSorted(values: string[]): string[] {
  return [...new Set(values.filter(Boolean))].sort((a, b) =>
    a.localeCompare(b, "en", { sensitivity: "base" }),
  );
}

function comparePolicies(a: PolicySummary, b: PolicySummary, sort: ColumnSort): number {
  switch (sort.key) {
    case "title":
      return compareText(a.title, b.title, sort.direction);
    case "document_id":
      return compareText(a.document_id, b.document_id, sort.direction);
    case "category":
      return compareText(a.category, b.category, sort.direction);
    case "department":
      return compareText(a.department, b.department, sort.direction);
    case "effective":
      return compareText(a.effective_date, b.effective_date, sort.direction);
    default:
      return 0;
  }
}

export function usePolicies() {
  const [policies, setPolicies] = useState<PolicySummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [columnFilters, setColumnFilters] =
    useState<PolicyColumnFilters>(DEFAULT_FILTERS);
  const [sort, setSort] = useState<ColumnSort | null>({
    key: "document_id",
    direction: "asc",
  });
  const [page, setPage] = useState(1);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await listPolicies(true);
        if (!cancelled) setPolicies(data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `API error (${err.status})`
              : "Could not load policies. Is the API running?",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  const filterOptions = useMemo(
    () => ({
      category: uniqueSorted(policies.map((policy) => policy.category)),
      department: uniqueSorted(policies.map((policy) => policy.department)),
    }),
    [policies],
  );

  const filtered = useMemo(() => {
    let rows = policies;
    if (columnFilters.category !== "all") {
      rows = rows.filter((policy) => policy.category === columnFilters.category);
    }
    if (columnFilters.department !== "all") {
      rows = rows.filter(
        (policy) => policy.department === columnFilters.department,
      );
    }

    const q = query.trim().toLowerCase();
    if (q) {
      rows = rows.filter((policy) => {
        const haystack = [
          policy.document_id,
          policy.title,
          policy.department,
          policy.category,
          policy.doc_type,
          policy.status,
        ]
          .join(" ")
          .toLowerCase();
        return haystack.includes(q);
      });
    }

    if (!sort) return rows;
    return [...rows].sort((a, b) => comparePolicies(a, b, sort));
  }, [policies, query, columnFilters, sort]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / POLICY_PAGE_SIZE));
  const safePage = Math.min(page, pageCount);

  useEffect(() => {
    setPage(1);
  }, [query, columnFilters, sort]);

  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  const pagePolicies = useMemo(() => {
    const start = (safePage - 1) * POLICY_PAGE_SIZE;
    return filtered.slice(start, start + POLICY_PAGE_SIZE);
  }, [filtered, safePage]);

  const rangeStart =
    filtered.length === 0 ? 0 : (safePage - 1) * POLICY_PAGE_SIZE + 1;
  const rangeEnd = Math.min(safePage * POLICY_PAGE_SIZE, filtered.length);

  function setColumnFilter<K extends keyof PolicyColumnFilters>(
    key: K,
    value: PolicyColumnFilters[K],
  ) {
    setColumnFilters((prev) => ({ ...prev, [key]: value }));
  }

  function toggleSort(key: string) {
    setSort((prev) => cycleSort(prev, key));
  }

  return {
    policies: pagePolicies,
    matchedCount: filtered.length,
    totalCount: policies.length,
    filterOptions,
    columnFilters,
    setColumnFilter,
    sort,
    toggleSort,
    loading,
    error,
    query,
    setQuery,
    page: safePage,
    setPage,
    pageCount,
    rangeStart,
    rangeEnd,
  };
}
