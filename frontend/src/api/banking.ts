import { apiGet } from "./http";
import type { Account, Client } from "./types";

export async function listClients(scenariosOnly = true): Promise<Client[]> {
  const query = scenariosOnly ? "?scenarios_only=true" : "";
  return apiGet<Client[]>(`/clients${query}`);
}

export async function getClient(clientRef: string): Promise<Client> {
  return apiGet<Client>(`/clients/${encodeURIComponent(clientRef)}`);
}

export async function getClientAccounts(clientRef: string): Promise<Account[]> {
  return apiGet<Account[]>(`/clients/${encodeURIComponent(clientRef)}/accounts`);
}
