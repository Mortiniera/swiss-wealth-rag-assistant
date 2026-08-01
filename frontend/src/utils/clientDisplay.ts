/** Human-readable open-item signal for directory rows. */
export function clientOpenItems(client: {
  kyc_profile: { status: string } | null;
}): string {
  const kyc = client.kyc_profile?.status?.toLowerCase();
  if (kyc === "expired") return "KYC expired";
  if (kyc === "pending" || kyc === "in_review") return "KYC pending";
  return "—";
}

/** True when the directory should treat the client as having an open ops item. */
export function hasClientOpenItem(client: {
  kyc_profile: { status: string } | null;
}): boolean {
  return clientOpenItems(client) !== "—";
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

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatMoney(
  amount: string | number | null | undefined,
  currency: string | null | undefined,
): string {
  if (amount == null || amount === "") return "—";
  const numeric = typeof amount === "number" ? amount : Number(amount);
  if (Number.isNaN(numeric)) return String(amount);
  try {
    return new Intl.NumberFormat("en-CH", {
      style: "currency",
      currency: currency || "CHF",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numeric);
  } catch {
    return `${numeric.toFixed(2)} ${currency ?? ""}`.trim();
  }
}

export type StatusTone = "neutral" | "info" | "warning" | "danger" | "success";

/** Tone for compliance / account / ops status chips. */
export function statusTone(status: string | null | undefined): StatusTone {
  const value = status?.toLowerCase() ?? "";
  if (
    ["expired", "blocked", "failed", "rejected", "breached", "cancelled"].includes(
      value,
    )
  ) {
    return "danger";
  }
  if (
    [
      "restricted",
      "pending",
      "pending_review",
      "in_review",
      "hold",
      "open",
      "high",
      "urgent",
    ].includes(value) ||
    value.includes("hold")
  ) {
    return "warning";
  }
  if (
    [
      "complete",
      "completed",
      "approved",
      "clear",
      "active",
      "booked",
      "resolved",
      "closed",
      "logged",
    ].includes(value)
  ) {
    return "success";
  }
  return "neutral";
}

/** True when an open service request has passed its SLA due time. */
export function isSlaBreached(
  status: string | null | undefined,
  slaDueAt: string | null | undefined,
): boolean {
  if (!slaDueAt) return false;
  const open = (status ?? "").toLowerCase() === "open";
  if (!open) return false;
  const due = new Date(slaDueAt);
  if (Number.isNaN(due.getTime())) return false;
  return due.getTime() < Date.now();
}
