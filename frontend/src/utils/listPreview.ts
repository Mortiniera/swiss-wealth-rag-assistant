/** Inline list preview size before “Show all” opens the full stack. */
export const PANEL_PREVIEW_LIMIT = 5;

export function takePreview<T>(items: T[], limit = PANEL_PREVIEW_LIMIT) {
  return {
    preview: items.slice(0, limit),
    hasMore: items.length > limit,
    remaining: Math.max(0, items.length - limit),
  };
}
