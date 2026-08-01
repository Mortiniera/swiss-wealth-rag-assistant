import { useEffect, useState } from "react";
import { AssistantDock } from "../assistant/AssistantDock";
import { WorkCanvas } from "../workspace/WorkCanvas";
import { DeploymentBanner } from "./DeploymentBanner";
import { Footer } from "./Footer";
import { NavRail } from "./NavRail";
import { TopBar } from "./TopBar";
import { useActorSession } from "../../hooks/useActorSession";
import type { NavId } from "../../types/workspace";
import type { SelectedClientContext } from "../../utils/personaView";

export function AppShell() {
  const { actors, workspace, loading, error, selectActor, actorCode } =
    useActorSession();
  const [activeNav, setActiveNav] = useState<NavId>("clients");
  const [dockOpen, setDockOpen] = useState(true);
  const [selectedClient, setSelectedClient] =
    useState<SelectedClientContext | null>(null);

  // Changing demo identity clears the open client — book/scope may differ.
  useEffect(() => {
    setSelectedClient(null);
  }, [actorCode]);

  async function handleActorChange(employeeCode: string) {
    await selectActor(employeeCode);
  }

  return (
    <div className="flex h-full min-h-svh flex-col animate-[shell-enter_360ms_cubic-bezier(0.22,1,0.36,1)_both]">
      <TopBar
        actors={actors}
        actorCode={actorCode}
        onActorChange={(code) => {
          void handleActorChange(code);
        }}
        actorLoading={loading}
        dockOpen={dockOpen}
        onToggleDock={() => setDockOpen((open) => !open)}
      />

      {workspace && (
        <div
          className="shrink-0 border-b border-border bg-accent-soft/70 px-4 py-1.5 sm:pl-16"
          role="status"
        >
          <p className="m-0 text-[0.8125rem] text-ink">
            <span className="font-semibold text-brand">Acting as </span>
            {workspace.actor.full_name}
            <span className="text-ink-tertiary"> · </span>
            {workspace.actor.role_name}
            <span className="text-ink-tertiary">
              {" "}
              — demo identity
              {workspace.client_scope === "assigned"
                ? " · assigned book"
                : " · full book"}
            </span>
          </p>
        </div>
      )}

      {error && (
        <p className="m-0 shrink-0 border-b border-[#efd2cd] bg-[#f8e8e6] px-4 py-2 text-[0.8125rem] text-danger sm:pl-16">
          {error}
        </p>
      )}

      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        <NavRail active={activeNav} onSelect={setActiveNav} />

        <main className="flex min-w-0 flex-1 flex-col overflow-auto bg-surface/40 px-4 py-4 sm:px-6 sm:py-5">
          <WorkCanvas
            activeNav={activeNav}
            workspace={workspace}
            selectedClient={selectedClient}
            onSelectedClientChange={setSelectedClient}
            actorReady={Boolean(workspace)}
            actorLoading={loading}
          />
          <div className="mt-auto pt-4">
            <DeploymentBanner />
            {!dockOpen && (
              <div className="mt-3">
                <Footer />
              </div>
            )}
          </div>
        </main>

        <AssistantDock
          open={dockOpen}
          onClose={() => setDockOpen(false)}
          clientContext={selectedClient}
        />
      </div>
    </div>
  );
}
