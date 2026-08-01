import type { NavId } from "../../types/workspace";
import { ClientsWorkspace } from "./ClientsWorkspace";
import { PoliciesWorkspace } from "./PoliciesWorkspace";

type WorkCanvasProps = {
  activeNav: NavId;
};

export function WorkCanvas({ activeNav }: WorkCanvasProps) {
  return (
    <section
      className="flex min-h-0 flex-1 flex-col animate-[canvas-fade_280ms_ease-out_both]"
      aria-label="Work area"
    >
      {activeNav === "clients" ? <ClientsWorkspace /> : <PoliciesWorkspace />}
    </section>
  );
}
