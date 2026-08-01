import { useEffect, useState } from "react";
import { ApiError, getPolicy, type PolicyDetail } from "../api/client";

export function usePolicyDetail(documentId: string | null) {
  const [policy, setPolicy] = useState<PolicyDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!documentId) {
      setPolicy(null);
      setError(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    async function load(id: string) {
      setLoading(true);
      setError(null);
      try {
        const detail = await getPolicy(id);
        if (!cancelled) setPolicy(detail);
      } catch (err) {
        if (!cancelled) {
          setPolicy(null);
          setError(
            err instanceof ApiError
              ? `API error (${err.status})`
              : "Could not load policy detail.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load(documentId);
    return () => {
      cancelled = true;
    };
  }, [documentId]);

  return { policy, loading, error };
}
