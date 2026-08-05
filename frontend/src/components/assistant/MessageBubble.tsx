import type { Message } from "../../types/chat";
import { EvidenceChips } from "./EvidenceChips";
import { MessageSources } from "./MessageSources";
import { RichText } from "./RichText";

type MessageBubbleProps = {
  message: Message;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const sourceCount = message.sources?.length ?? 0;
  const evidence = message.evidence ?? [];

  return (
    <div className={`mb-4 flex flex-col px-1 ${isUser ? "items-end" : "items-stretch"}`}>
      {isUser ? (
        <div className="max-w-[94%] bg-brand px-3 py-2 text-[0.8375rem] leading-[1.5] whitespace-pre-wrap text-white">
          {message.content}
        </div>
      ) : (
        <div className="w-full">
          <RichText
            content={message.content}
            messageId={message.timestamp}
            sourceCount={sourceCount}
          />
          <EvidenceChips evidence={evidence} />
          {!isUser && message.traceUrl && (
            <p className="mt-2 text-[0.6875rem]">
              <a
                href={message.traceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-brand underline decoration-brand/40 underline-offset-2 hover:decoration-brand"
              >
                View Langfuse trace
              </a>
            </p>
          )}
        </div>
      )}

      {!isUser && message.sources && message.sources.length > 0 && (
        <MessageSources sources={message.sources} messageId={message.timestamp} />
      )}
    </div>
  );
}
