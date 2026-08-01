import { useEffect, useState } from "react";
import {
  ApiError,
  getClient,
  getClientAccounts,
  type Account,
  type Client,
} from "../api/client";

export function useClientDetail(clientRef: string | null) {
  const [client, setClient] = useState<Client | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!clientRef) {
      setClient(null);
      setAccounts([]);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function load(ref: string) {
      setLoading(true);
      setError(null);
      try {
        const [profile, accountRows] = await Promise.all([
          getClient(ref),
          getClientAccounts(ref),
        ]);
        if (!cancelled) {
          setClient(profile);
          setAccounts(accountRows);
        }
      } catch (err) {
        if (!cancelled) {
          setClient(null);
          setAccounts([]);
          setError(
            err instanceof ApiError
              ? `API error (${err.status})`
              : "Could not load client detail.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load(clientRef);
    return () => {
      cancelled = true;
    };
  }, [clientRef]);

  return { client, accounts, loading, error };
}
