import { useEffect, useMemo, useState } from "react";
import { ApiError, listClients, type Client } from "../api/client";

export type ClientListFilter = "all" | "scenarios";

function isScenarioClient(client: Client): boolean {
  return client.client_code.startsWith("CLI-SCEN-");
}

export function useClients() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [listFilter, setListFilter] = useState<ClientListFilter>("all");

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

  return {
    clients: filtered,
    totalCount: clients.length,
    scenarioCount,
    loading,
    error,
    query,
    setQuery,
    listFilter,
    setListFilter,
  };
}
