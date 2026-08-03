import type { Source, EvidenceItem } from "../api/client";

export type ChatRole = "user" | "assistant";

export type Message = {
  role: ChatRole;
  content: string;
  sources?: Source[];
  evidence?: EvidenceItem[];
  timestamp: string;
};
