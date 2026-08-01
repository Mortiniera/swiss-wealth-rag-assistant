import { useState } from "react";
import { askQuestion, ApiError, type ChatMessage } from "../api/client";
import type { Message } from "../types/chat";
import {
  withClientContext,
  type SelectedClientContext,
} from "../utils/personaView";

function nowIso() {
  return new Date().toISOString();
}

function toApiHistory(messages: Message[]): ChatMessage[] {
  return messages.map((message) => ({
    role: message.role,
    content: message.content,
  }));
}

export function useChat(clientContext: SelectedClientContext | null = null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function reset() {
    if (loading) return;
    setMessages([]);
    setError(null);
  }

  async function ask(question: string) {
    setError(null);

    const history = toApiHistory(messages);
    const userMessage: Message = {
      role: "user",
      content: question,
      timestamp: nowIso(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const wireQuestion = withClientContext(question, clientContext);
      const data = await askQuestion(wireQuestion, history);
      const assistantMessage: Message = {
        role: "assistant",
        content: data.answer,
        sources: data.sources,
        timestamp: nowIso(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `API error (${err.status})`
          : "Something went wrong. Check the API is running and CORS is configured.",
      );
    } finally {
      setLoading(false);
    }
  }

  return {
    messages,
    loading,
    error,
    hasConversation: messages.length > 0,
    ask,
    reset,
  };
}
