import type { Source } from "../api/client";

export type ChatRole = "user" | "assistant";

export type Message = {
  role: ChatRole;
  content: string;
  sources?: Source[];
  timestamp: string;
};
