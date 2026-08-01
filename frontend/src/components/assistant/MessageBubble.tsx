import type { Message } from "../../types/chat";
import { MessageSources } from "./MessageSources";
import { RichText } from "./RichText";

type MessageBubbleProps = {
  message: Message;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const sourceCount = message.sources?.length ?? 0;

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
        </div>
      )}

      {!isUser && message.sources && message.sources.length > 0 && (
        <MessageSources sources={message.sources} messageId={message.timestamp} />
      )}
    </div>
  );
}
