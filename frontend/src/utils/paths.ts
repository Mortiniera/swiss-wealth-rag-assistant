/** Last path segment for display (e.g. POL-RST-001.md). */
export function fileName(path: string): string {
  return path.split("/").pop() ?? path;
}
