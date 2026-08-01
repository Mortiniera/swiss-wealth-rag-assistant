import { apiGet } from "./http";
import type { PolicyDetail, PolicySummary } from "./types";

export async function listPolicies(activeOnly = true): Promise<PolicySummary[]> {
  const query = activeOnly ? "?active_only=true" : "?active_only=false";
  return apiGet<PolicySummary[]>(`/policies${query}`);
}

export async function getPolicy(documentId: string): Promise<PolicyDetail> {
  return apiGet<PolicyDetail>(`/policies/${encodeURIComponent(documentId)}`);
}
