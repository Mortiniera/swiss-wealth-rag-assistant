import { useEffect, useMemo, useState } from "react";
import { ApiError, listClients, type Client } from "../api/client";
import {
  clientOpenItemList,
  clientOpenItems,
  hasClientOpenItem,
} from "../utils/clientDisplay";
import {
  compareText,
  cycleSort,
  type ColumnSort,
} from "../utils/tableSort";

export type ClientListFilter = "all" | "scenarios";

/** Rows per directory page — ops-readable, not an endless dump. */
export const CLIENT_PAGE_SIZE = 25;

export type ClientColumnFilters = {
  rm: string;
  risk: string;
  openItem: string;
};

const DEFAULT_FILTERS: ClientColumnFilters = {
  rm: "all",
  risk: "all",
  openItem: "all",
};

function isScenarioClient(client: Client): boolean {
  return client.client_code.startsWith("CLI-SCEN-");
}

function riskValue(client: Client): string {
  return client.suitability_profile?.risk_profile ?? "";
}

function rmValue(client: Client): string {
  return client.primary_assignment?.full_name ?? "";
}

function openItemValue(client: Client): string {
  return clientOpenItems(client);
}

function uniqueSorted(values: string[]): string[] {
  return [...new Set(values.filter(Boolean))].sort((a, b) =>
    a.localeCompare(b, "en", { sensitivity: "base" }),
  );
}

function compareClients(a: Client, b: Client, sort: ColumnSort): number {
  switch (sort.key) {
    case "name":
      return compareText(a.full_name, b.full_name, sort.direction);
    case "code":
      return compareText(a.client_code, b.client_code, sort.direction);
    case "rm":
      return compareText(rmValue(a) || "—", rmValue(b) || "—", sort.direction);
    case "risk":
      return compareText(riskValue(a) || "—", riskValue(b) || "—", sort.direction);
    case "openItem": {
      const openDelta =
        Number(hasClientOpenItem(b)) - Number(hasClientOpenItem(a));
      if (openDelta !== 0) {
        return sort.direction === "asc" ? -openDelta : openDelta;
      }
      return compareText(openItemValue(a), openItemValue(b), sort.direction);
    }
    default:
      return 0;
  }
}

export function useClients(actorCode: string | null = null) {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [listFilter, setListFilter] = useState<ClientListFilter>("all");
  const [columnFilters, setColumnFilters] =
    useState<ClientColumnFilters>(DEFAULT_FILTERS);
  const [sort, setSort] = useState<ColumnSort | null>({
    key: "name",
    direction: "asc",
  });
  const [page, setPage] = useState(1);

  useEffect(() => {
    setListFilter("all");
    setColumnFilters(DEFAULT_FILTERS);
    setQuery("");
    setPage(1);
    setSort((prev) =>
      prev?.key === "rm" ? { key: "name", direction: "asc" } : prev,
    );
  }, [actorCode]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await listClients(false);
        if (!cancelled) setClients(data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `API error (${err.status})`
              : "Could not load clients. Is the API running?",
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
  }, [actorCode]);

  const scenarioCount = useMemo(
    () => clients.filter(isScenarioClient).length,
    [clients],
  );

  useEffect(() => {
    if (scenarioCount === 0 && listFilter === "scenarios") {
      setListFilter("all");
    }
  }, [scenarioCount, listFilter]);

  const scoped = useMemo(() => {
    return listFilter === "scenarios"
      ? clients.filter(isScenarioClient)
      : clients;
  }, [clients, listFilter]);

  const filterOptions = useMemo(
    () => ({
      rm: uniqueSorted(scoped.map(rmValue)),
      risk: uniqueSorted(scoped.map(riskValue)),
      openItem: uniqueSorted(
        scoped.flatMap((client) => clientOpenItemList(client)),
      ),
    }),
    [scoped],
  );

  const filtered = useMemo(() => {
    let rows = scoped;

    if (columnFilters.rm !== "all") {
      rows = rows.filter((client) => rmValue(client) === columnFilters.rm);
    }
    if (columnFilters.risk !== "all") {
      rows = rows.filter((client) => riskValue(client) === columnFilters.risk);
    }
    if (columnFilters.openItem !== "all") {
      rows = rows.filter((client) =>
        clientOpenItemList(client).includes(columnFilters.openItem),
      );
    }

    const q = query.trim().toLowerCase();
    if (q) {
      rows = rows.filter((client) => {
        const haystack = [
          client.client_code,
          client.full_name,
          rmValue(client),
          riskValue(client),
          ...clientOpenItemList(client),
        ]
          .join(" ")
          .toLowerCase();
        return haystack.includes(q);
      });
    }

    if (!sort) return rows;
    return [...rows].sort((a, b) => compareClients(a, b, sort));
  }, [scoped, query, columnFilters, sort]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / CLIENT_PAGE_SIZE));
  const safePage = Math.min(page, pageCount);

  useEffect(() => {
    setPage(1);
  }, [query, listFilter, columnFilters, sort]);

  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  const pageClients = useMemo(() => {
    const start = (safePage - 1) * CLIENT_PAGE_SIZE;
    return filtered.slice(start, start + CLIENT_PAGE_SIZE);
  }, [filtered, safePage]);

  const rangeStart =
    filtered.length === 0 ? 0 : (safePage - 1) * CLIENT_PAGE_SIZE + 1;
  const rangeEnd = Math.min(safePage * CLIENT_PAGE_SIZE, filtered.length);

  function setColumnFilter<K extends keyof ClientColumnFilters>(
    key: K,
    value: ClientColumnFilters[K],
  ) {
    setColumnFilters((prev) => ({ ...prev, [key]: value }));
  }

  function toggleSort(key: string) {
    setSort((prev) => cycleSort(prev, key));
  }

  return {
    clients: pageClients,
    matchedCount: filtered.length,
    totalCount: clients.length,
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
    page: safePage,
    setPage,
    pageCount,
    pageSize: CLIENT_PAGE_SIZE,
    rangeStart,
    rangeEnd,
  };
}
