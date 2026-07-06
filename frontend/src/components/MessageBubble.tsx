import type { Source } from "../api/client";
import { renderTextWithCitations } from "../utils/renderCitations";
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

function renderParagraphs(content: string, messageId: string, sourceCount = 0) {
    const paragraphs = content.split(/\n\n+/).filter(Boolean);
    const useCitations = sourceCount > 0;

    if (paragraphs.length <= 1) {
        return (
            <p>
                {useCitations
                    ? renderTextWithCitations(content, messageId, sourceCount)
                    : content}
            </p>
        );
    }

    return paragraphs.map((paragraph, index) => (
        <p key={index}>
            {useCitations
                ? renderTextWithCitations(paragraph, messageId, sourceCount)
                : paragraph}
        </p>
    ));
}

export function MessageBubble({ message }: MessageBubbleProps) {
    const isUser = message.role === "user";
    const sourceCount = message.sources?.length ?? 0;

    return (
        <div className={`message ${isUser ? "message--user" : "message--assistant"}`}>
            <div className="message__bubble">
                <div className="message__content">
                    {renderParagraphs(message.content, message.timestamp, sourceCount)}
                </div>
            </div>

            {!isUser && message.sources && message.sources.length > 0 && (
                <div className="message__sources">
                    <p className="message__sources-label">References</p>
                    <ol className="source-list">
                        {message.sources.map((source, index) => (
                            <li key={source.chunk_id} className="source-list__item">
                                <SourceCard
                                    source={source}
                                    index={index + 1}
                                    anchorId={`source-${message.timestamp}-${index + 1}`}
                                />
                            </li>
                        ))}
                    </ol>
                </div>
            )}
        </div>
    );
}
