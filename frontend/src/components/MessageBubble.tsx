import type { Source } from "../api/client";
import { SourceCard } from "./SourceCard";

export type Message = {
    role: "user" | "assistant";
    content: string;
    sources?: Source[];
    timestamp: string;
};

type MessageBubbleProps = {
    message: Message;
};

export function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.role === "user";

    return (
        <div className={`message ${isUser ? "message--user" : "message--assistant"}`}>
            <div className="message__bubble">
                <p>{message.content}</p>
            </div>

            {!isUser && message.sources && message.sources.length > 0 && (
                <div className="message__sources">
                    <p className="message__sources-label">Sources</p>
                    <div className="source-grid">
                        {message.sources.map((source) => (
                            <SourceCard key={source.chunk_id} source={source} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}