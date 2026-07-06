import { useState } from "react";
import { askQuestion, ApiError, type ChatMessage } from "../api/client";
import { ExamplePrompts } from "./ExamplePrompts";
import { LoadingState } from "./LoadingState";
import { MessageBubble, type Message } from "./MessageBubble";
import { QueryInput } from "./QueryInput";

function nowIso() {
    return new Date().toISOString();
}

function toApiHistory(messages: Message[]): ChatMessage[] {
    return messages.map((message) => ({
        role: message.role,
        content: message.content,
    }));
}

export function ChatWindow() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    function handleNewConversation() {
        if (loading) return;
        setMessages([]);
        setError(null);
    }

    async function handleAsk(question: string) {
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
            const data = await askQuestion(question, history);
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

    const hasConversation = messages.length > 0;

    return (
        <div className="chat-window">
            {hasConversation && (
                <div className="chat-window__toolbar">
                    <button
                        type="button"
                        className="chat-window__reset"
                        onClick={handleNewConversation}
                        disabled={loading}
                    >
                        New conversation
                    </button>
                </div>
            )}

            <div className="chat-window__messages">
                {!hasConversation && !loading && (
                    <ExamplePrompts onSelect={handleAsk} disabled={loading} />
                )}

                {messages.map((message, index) => (
                    <MessageBubble key={`${message.timestamp}-${index}`} message={message} />
                ))}

                {loading && <LoadingState />}
                {error && <p className="chat-window__error">{error}</p>}
            </div>

            <QueryInput onSubmit={handleAsk} disabled={loading} />
        </div>
    );
}
