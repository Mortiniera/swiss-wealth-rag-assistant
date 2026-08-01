import { useState } from "react";
import { AssistantDock } from "../assistant/AssistantDock";
import { WorkCanvas } from "../workspace/WorkCanvas";
import { DeploymentBanner } from "./DeploymentBanner";
import { Footer } from "./Footer";
import { NavRail } from "./NavRail";
import { TopBar } from "./TopBar";
import type { NavId, PersonaId } from "../../types/workspace";

export function AppShell() {
  const [persona, setPersona] = useState<PersonaId>("rm");
  const [activeNav, setActiveNav] = useState<NavId>("clients");
  const [dockOpen, setDockOpen] = useState(true);

  return (
    <div className="flex h-full min-h-svh flex-col animate-[shell-enter_360ms_cubic-bezier(0.22,1,0.36,1)_both]">
      <TopBar
        persona={persona}
        onPersonaChange={setPersona}
        dockOpen={dockOpen}
        onToggleDock={() => setDockOpen((open) => !open)}
      />

      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        <NavRail active={activeNav} onSelect={setActiveNav} />

        <main className="flex min-w-0 flex-1 flex-col overflow-auto bg-surface/40 px-4 py-4 sm:px-6 sm:py-5">
          <WorkCanvas activeNav={activeNav} />
          <div className="mt-auto pt-4">
            <DeploymentBanner />
            {!dockOpen && (
              <div className="mt-3">
                <Footer />
              </div>
            )}
          </div>
        </main>

        <AssistantDock open={dockOpen} onClose={() => setDockOpen(false)} />
      </div>
    </div>
  );
}
