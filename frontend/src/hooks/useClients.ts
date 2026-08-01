import { useEffect, useMemo, useState } from "react";
import { ApiError, listClients, type Client } from "../api/client";

export type ClientListFilter = "all" | "scenarios";

/** Rows per directory page — ops-readable, not an endless dump. */
export const CLIENT_PAGE_SIZE = 25;

function isScenarioClient(client: Client): boolean {
  return client.client_code.startsWith("CLI-SCEN-");
}

export function useClients() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [listFilter, setListFilter] = useState<ClientListFilter>("all");
  const [page, setPage] = useState(1);

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
  }, []);

  const filtered = useMemo(() => {
    const base =
      listFilter === "scenarios" ? clients.filter(isScenarioClient) : clients;
    const q = query.trim().toLowerCase();
    if (!q) return base;
    return base.filter((client) => {
      const haystack = [
        client.client_code,
        client.full_name,
        client.primary_assignment?.full_name ?? "",
        client.kyc_profile?.status ?? "",
        client.suitability_profile?.risk_profile ?? "",
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    });
  }, [clients, query, listFilter]);

  const scenarioCount = useMemo(
    () => clients.filter(isScenarioClient).length,
    [clients],
  );

  const pageCount = Math.max(1, Math.ceil(filtered.length / CLIENT_PAGE_SIZE));
  const safePage = Math.min(page, pageCount);

  useEffect(() => {
    setPage(1);
  }, [query, listFilter]);

  useEffect(() => {
    if (page > pageCount) setPage(pageCount);
  }, [page, pageCount]);

  const pageClients = useMemo(() => {
    const start = (safePage - 1) * CLIENT_PAGE_SIZE;
    return filtered.slice(start, start + CLIENT_PAGE_SIZE);
  }, [filtered, safePage]);

  const rangeStart = filtered.length === 0 ? 0 : (safePage - 1) * CLIENT_PAGE_SIZE + 1;
  const rangeEnd = Math.min(safePage * CLIENT_PAGE_SIZE, filtered.length);

  return {
    clients: pageClients,
    matchedCount: filtered.length,
    totalCount: clients.length,
    scenarioCount,
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
