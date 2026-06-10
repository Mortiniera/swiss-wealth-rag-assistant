import { useState } from "react";
import { askQuestion, ApiError } from "../api/client";
import { MessageBubble, type Message } from "./MessageBubble";
import { QueryInput } from "./QueryInput";

function nowIso() {
    return new Date().toISOString();
}

export function ChatWindow() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function handleAsk(question: string) {
        setError(null);

        const userMessage: Message = {
            role: "user",
            content: question,
            timestamp: nowIso(),
        };
        setMessages((prev) => [...prev, userMessage]);
        setLoading(true);

        try {
            const data = await askQuestion(question);
            const assistantMessage: Message = {
                role: "assistant",
                content: data.answer,
                sources: data.sources,
                timestamp: nowIso(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (err) {
            const message =
                err instanceof ApiError
                    ? `API error (${err.status})`
                    : "Something went wrong. Check the API is running and CORS is configured.";
            setError(message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="chat-window">
            <div className="chat-window__messages">
                {messages.length === 0 && (
                    <p className="chat-window__empty">
                        Ask a question about sustainable investing, family governance, private banking, or
                        wealth planning.
                    </p>
                )}

                {messages.map((message, index) => (
                    <MessageBubble key={`${message.timestamp}-${index}`} message={message} />
                ))}

                {loading && <p className="chat-window__loading">Retrieving sources and generating answer...</p>}
                {error && <p className="chat-window__error">{error}</p>}
            </div>

            <QueryInput onSubmit={handleAsk} disabled={loading} />
        </div>
    );
}