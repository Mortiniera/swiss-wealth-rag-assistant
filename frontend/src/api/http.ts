/** Shared Helvetia API fetch helpers with optional demo-actor header. */

import { ApiError } from "./errors";

export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const ACTOR_HEADER = "X-Helvetia-Actor";

let actorCode: string | null = null;

export function setApiActorCode(code: string | null) {
  actorCode = code;
}

export function getApiActorCode(): string | null {
  return actorCode;
}

function actorHeaders(extra?: HeadersInit): Headers {
  const headers = new Headers(extra);
  if (actorCode) {
    headers.set(ACTOR_HEADER, actorCode);
  }
  return headers;
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: actorHeaders(),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new ApiError(detail || `Request failed (${response.status})`, response.status);
  }
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: actorHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new ApiError(detail || `Request failed (${response.status})`, response.status);
  }
  return response.json() as Promise<T>;
}
