export type SortDirection = "asc" | "desc";

export type ColumnSort = {
  key: string;
  direction: SortDirection;
};

/** Cycle sort: new column → asc → desc → clear. */
export function cycleSort(current: ColumnSort | null, key: string): ColumnSort | null {
  if (!current || current.key !== key) return { key, direction: "asc" };
  if (current.direction === "asc") return { key, direction: "desc" };
  return null;
}

export function compareText(a: string, b: string, direction: SortDirection): number {
  const result = a.localeCompare(b, "en", { sensitivity: "base" });
  return direction === "asc" ? result : -result;
}
