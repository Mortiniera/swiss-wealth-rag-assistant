/** Human-readable open-item signal for directory rows. */
export function clientOpenItems(client: {
  kyc_profile: { status: string } | null;
}): string {
  const kyc = client.kyc_profile?.status?.toLowerCase();
  if (kyc === "expired") return "KYC expired";
  if (kyc === "pending" || kyc === "in_review") return "KYC pending";
  return "—";
}

export function formatLabel(value: string | null | undefined): string {
  if (!value) return "—";
  const normalized = value.replaceAll("_", " ");
  if (normalized.toLowerCase() === "hnwi") return "HNWI";
  if (normalized.toLowerCase() === "uhnw") return "UHNW";
  return normalized;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export type StatusTone = "neutral" | "info" | "warning" | "danger" | "success";

/** Tone for compliance / account status chips. */
export function statusTone(status: string | null | undefined): StatusTone {
  const value = status?.toLowerCase() ?? "";
  if (["expired", "blocked", "failed", "rejected", "breached"].includes(value)) {
    return "danger";
  }
  if (["restricted", "pending", "in_review", "hold"].includes(value) || value.includes("hold")) {
    return "warning";
  }
  if (["complete", "approved", "clear", "active"].includes(value)) {
    return "success";
  }
  return "neutral";
}
