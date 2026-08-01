export type NavId = "clients" | "policies";

export const NAV_ITEMS: { id: NavId; label: string; short: string }[] = [
  { id: "clients", label: "Clients", short: "Cl" },
  { id: "policies", label: "Policies", short: "Po" },
];
