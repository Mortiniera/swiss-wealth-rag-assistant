import { useEffect, useState } from "react";
import {
  ApiError,
  getClient,
  getClientAccounts,
  getClientInteractions,
  getClientServiceRequests,
  getClientTransactions,
  type Account,
  type Client,
  type Interaction,
  type ServiceRequest,
  type Transaction,
} from "../api/client";

export function useClientDetail(clientRef: string | null) {
  const [client, setClient] = useState<Client | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [serviceRequests, setServiceRequests] = useState<ServiceRequest[]>([]);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!clientRef) {
      setClient(null);
      setAccounts([]);
      setTransactions([]);
      setServiceRequests([]);
      setInteractions([]);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function load(ref: string) {
      setLoading(true);
      setError(null);
      try {
        const [profile, accountRows, txnRows, srqRows, interactionRows] =
          await Promise.all([
            getClient(ref),
            getClientAccounts(ref),
            getClientTransactions(ref),
            getClientServiceRequests(ref),
            getClientInteractions(ref),
          ]);
        if (!cancelled) {
          setClient(profile);
          setAccounts(accountRows);
          setTransactions(txnRows);
          setServiceRequests(srqRows);
          setInteractions(interactionRows);
        }
      } catch (err) {
        if (!cancelled) {
          setClient(null);
          setAccounts([]);
          setTransactions([]);
          setServiceRequests([]);
          setInteractions([]);
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

  return {
    client,
    accounts,
    transactions,
    serviceRequests,
    interactions,
    loading,
    error,
  };
}
