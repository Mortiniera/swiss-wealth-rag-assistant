import { apiGet } from "./http";
import type {
  Account,
  Client,
  Interaction,
  ServiceRequest,
  Transaction,
} from "./types";

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

export async function getClientTransactions(
  clientRef: string,
): Promise<Transaction[]> {
  return apiGet<Transaction[]>(
    `/clients/${encodeURIComponent(clientRef)}/transactions`,
  );
}

export async function getClientInteractions(
  clientRef: string,
): Promise<Interaction[]> {
  return apiGet<Interaction[]>(
    `/clients/${encodeURIComponent(clientRef)}/interactions`,
  );
}

export async function getClientServiceRequests(
  clientRef: string,
): Promise<ServiceRequest[]> {
  return apiGet<ServiceRequest[]>(
    `/clients/${encodeURIComponent(clientRef)}/service-requests`,
  );
}