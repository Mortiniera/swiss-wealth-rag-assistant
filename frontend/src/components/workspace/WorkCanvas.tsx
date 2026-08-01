import type { NavId } from "../../types/workspace";
import { DataTable, EmptyState, SearchField } from "../ui";
import { ClientsWorkspace } from "./ClientsWorkspace";
import { PageHeader } from "./PageHeader";

type WorkCanvasProps = {
  activeNav: NavId;
};

export function WorkCanvas({ activeNav }: WorkCanvasProps) {
  if (activeNav === "clients") {
    return (
      <section
        className="flex min-h-0 flex-1 flex-col animate-[canvas-fade_280ms_ease-out_both]"
        aria-label="Work area"
      >
        <ClientsWorkspace />
      </section>
    );
  }

  return (
    <section
      className="flex min-h-0 flex-1 flex-col animate-[canvas-fade_280ms_ease-out_both]"
      aria-label="Work area"
    >
      <PageHeader
        title="Policies"
        description="Active Helvetia policies for KYC, transfers, AML, and restrictions."
        actions={
          <SearchField
            disabled
            placeholder="Search policies"
            aria-label="Search policies"
          />
        }
      />
      <DataTable columns={["Document", "Domain", "Status", "Effective"]}>
        <EmptyState
          title="No policy selected"
          description="Select a policy to review metadata and summary."
        />
      </DataTable>
    </section>
  );
}
