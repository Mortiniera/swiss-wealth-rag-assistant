import { Badge } from "../ui";
import type { EvidenceItem } from "../../api/client";

type EvidenceChipsProps = {
  evidence: EvidenceItem[];
};

function toneFor(label: string, value: string): "neutral" | "warning" | "danger" | "info" {
  const v = value.toLowerCase();
  const l = label.toLowerCase();
  if (l === "kyc" && (v.includes("expired") || v.includes("refresh"))) {
    return v.includes("expired") ? "danger" : "warning";
  }
  if (l === "restriction") {
    return "warning";
  }
  if (l === "pending txn" || l === "delay") {
    return v.includes("none") ? "neutral" : "warning";
  }
  if (l === "open sr") {
    return v.includes("none") ? "neutral" : "warning";
  }
  if (l === "interaction" || l === "inbound") {
    return v.includes("none") ? "neutral" : "warning";
  }
  if (l === "transactions" && v.includes("none")) {
    return "neutral";
  }
  if (l === "holdings" || l === "position") {
    return v.includes("none") ? "neutral" : "info";
  }
  return "neutral";
}

export function EvidenceChips({ evidence }: EvidenceChipsProps) {
  if (evidence.length === 0) return null;

  return (
    <div
      className="mt-2 flex flex-wrap gap-1.5"
      aria-label="Structured client evidence"
    >
      {evidence.map((item) => (
        <Badge key={`${item.label}-${item.value}`} tone={toneFor(item.label, item.value)}>
          {item.label}: {item.value}
        </Badge>
      ))}
    </div>
  );
}
