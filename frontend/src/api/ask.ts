import { apiPost } from "./http";
import type { AskResponse, ChatMessage } from "./types";

export async function askQuestion(
  question: string,
  history: ChatMessage[] = [],
): Promise<AskResponse> {
  return apiPost<AskResponse>("/ask", { question, history });
}
