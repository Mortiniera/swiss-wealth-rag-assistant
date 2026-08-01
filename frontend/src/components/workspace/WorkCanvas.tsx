import type { NavId } from "../../types/workspace";
import { DataTable, EmptyState, SearchField } from "../ui";
import { PageHeader } from "./PageHeader";

type WorkCanvasProps = {
  activeNav: NavId;
};

type ViewConfig = {
  title: string;
  description: string;
  columns: readonly string[];
  searchPlaceholder: string;
  emptyTitle: string;
  emptyDescription: string;
};

const VIEWS: Record<NavId, ViewConfig> = {
  clients: {
    title: "Clients",
    description: "Scenario clients for service, KYC, and transfer review.",
    columns: ["Client", "Relationship manager", "Risk", "Open items"],
    searchPlaceholder: "Search clients",
    emptyTitle: "No client selected",
    emptyDescription: "Select a client to inspect profile, accounts, and open items.",
  },
  policies: {
    title: "Policies",
    description: "Active Helvetia policies for KYC, transfers, AML, and restrictions.",
    columns: ["Document", "Domain", "Status", "Effective"],
    searchPlaceholder: "Search policies",
    emptyTitle: "No policy selected",
    emptyDescription: "Select a policy to review metadata and summary.",
  },
};

export function WorkCanvas({ activeNav }: WorkCanvasProps) {
  const view = VIEWS[activeNav];

  return (
    <section
      className="flex min-h-0 flex-1 flex-col animate-[canvas-fade_280ms_ease-out_both]"
      aria-label="Work area"
    >
      <PageHeader
        title={view.title}
        description={view.description}
        actions={
          <SearchField
            disabled
            placeholder={view.searchPlaceholder}
            aria-label={view.searchPlaceholder}
          />
        }
      />

      <DataTable columns={view.columns}>
        <EmptyState title={view.emptyTitle} description={view.emptyDescription} />
      </DataTable>
    </section>
  );
}
