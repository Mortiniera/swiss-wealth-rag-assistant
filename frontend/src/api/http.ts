import { ApiError } from "./errors";

export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    const detail = await response.text();
    throw new ApiError(detail || `Request failed (${response.status})`, response.status);
  }
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new ApiError(detail || `Request failed (${response.status})`, response.status);
  }
  return response.json() as Promise<T>;
}
