import { useEffect, useState } from "react";
import {
  ApiError,
  getActorWorkspace,
  listActors,
  setApiActorCode,
  type Actor,
  type WorkspaceContext,
} from "../api/client";

/** Prefer Elena (EMP-0001) — owns the CLI-SCEN-* flagship book; else first RM. */
const FLAGSHIP_RM_CODE = "EMP-0001";

function pickDefaultActor(actors: Actor[]): Actor | null {
  if (actors.length === 0) return null;
  return (
    actors.find((actor) => actor.employee_code === FLAGSHIP_RM_CODE) ??
    actors.find((actor) => actor.role_code === "relationship_manager") ??
    actors[0]
  );
}

export function useActorSession() {
  const [actors, setActors] = useState<Actor[]>([]);
  const [workspace, setWorkspace] = useState<WorkspaceContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function boot() {
      setLoading(true);
      setError(null);
      try {
        const rows = await listActors();
        if (cancelled) return;
        setActors(rows);
        const initial = pickDefaultActor(rows);
        if (!initial) {
          setWorkspace(null);
          setApiActorCode(null);
          setError(
            "No demo employees in the database. Seed structured data (scripts/seed_db.py) on the API host.",
          );
          return;
        }
        setApiActorCode(initial.employee_code);
        const context = await getActorWorkspace(initial.employee_code);
        if (!cancelled) setWorkspace(context);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `API error (${err.status})`
              : "Could not load demo actors.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void boot();
    return () => {
      cancelled = true;
    };
  }, []);

  async function selectActor(employeeCode: string) {
    setError(null);
    setApiActorCode(employeeCode);
    setLoading(true);
    try {
      const context = await getActorWorkspace(employeeCode);
      setWorkspace(context);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `API error (${err.status})`
          : "Could not load actor workspace.",
      );
    } finally {
      setLoading(false);
    }
  }

  return {
    actors,
    workspace,
    loading,
    error,
    selectActor,
    actorCode: workspace?.actor.employee_code ?? null,
  };
}
