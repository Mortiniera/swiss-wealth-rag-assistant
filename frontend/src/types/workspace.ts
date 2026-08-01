export type PersonaId = "rm" | "client_service" | "compliance";

export type NavId = "clients" | "policies";

export const PERSONAS: { id: PersonaId; label: string }[] = [
  { id: "rm", label: "Relationship Manager" },
  { id: "client_service", label: "Client Service" },
  { id: "compliance", label: "Compliance viewer" },
];

export const NAV_ITEMS: { id: NavId; label: string; short: string }[] = [
  { id: "clients", label: "Clients", short: "Cl" },
  { id: "policies", label: "Policies", short: "Po" },
];
