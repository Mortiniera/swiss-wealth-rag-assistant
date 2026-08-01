import { apiGet } from "./http";
import type { Actor, WorkspaceContext } from "./types";

export async function listActors(): Promise<Actor[]> {
  return apiGet<Actor[]>("/actors");
}

export async function getActorWorkspace(
  employeeCode: string,
): Promise<WorkspaceContext> {
  return apiGet<WorkspaceContext>(
    `/actors/${encodeURIComponent(employeeCode)}/workspace`,
  );
}
