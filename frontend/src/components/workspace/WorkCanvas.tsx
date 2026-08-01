import type { NavId } from "../../types/workspace";
import type { WorkspaceContext } from "../../api/client";
import type { SelectedClientContext } from "../../utils/personaView";
import { ClientsWorkspace } from "./ClientsWorkspace";
import { PoliciesWorkspace } from "./PoliciesWorkspace";

type WorkCanvasProps = {
  activeNav: NavId;
  workspace: WorkspaceContext | null;
  selectedClient: SelectedClientContext | null;
  onSelectedClientChange: (client: SelectedClientContext | null) => void;
  actorReady: boolean;
};

export function WorkCanvas({
  activeNav,
  workspace,
  selectedClient,
  onSelectedClientChange,
  actorReady,
}: WorkCanvasProps) {
  if (!actorReady || !workspace) {
    return (
      <section
        className="flex min-h-0 flex-1 flex-col"
        aria-label="Work area"
      >
        <p className="text-[0.875rem] text-ink-secondary">
          Loading demo operator identity…
        </p>
      </section>
    );
  }

  return (
    <section
      className="flex min-h-0 flex-1 flex-col animate-[canvas-fade_280ms_ease-out_both]"
      aria-label="Work area"
    >
      {activeNav === "clients" ? (
        <ClientsWorkspace
          workspace={workspace}
          selectedClient={selectedClient}
          onSelectedClientChange={onSelectedClientChange}
        />
      ) : (
        <PoliciesWorkspace actorCode={workspace.actor.employee_code} />
      )}
    </section>
  );
}
