import { useChat } from "../../hooks/useChat";
import type { SelectedClientContext } from "../../utils/personaView";
import { cn } from "../../utils/cn";
import { ExamplePrompts } from "./ExamplePrompts";
import { LoadingState } from "./LoadingState";
import { MessageBubble } from "./MessageBubble";
import { QueryInput } from "./QueryInput";

type ChatWindowProps = {
  compact?: boolean;
  clientContext?: SelectedClientContext | null;
};

export function ChatWindow({
  compact = false,
  clientContext = null,
}: ChatWindowProps) {
  const { messages, loading, error, hasConversation, ask, reset } =
    useChat(clientContext);

  return (
    <div className={cn("flex min-h-0 flex-1 flex-col", compact ? "gap-2" : "gap-3")}>
      {hasConversation && (
        <div className="flex shrink-0 justify-end">
          <button
            type="button"
            className="text-[0.75rem] font-medium text-ink-tertiary transition-colors hover:text-brand disabled:opacity-50"
            onClick={reset}
            disabled={loading}
          >
            New conversation
          </button>
        </div>
      )}

      <div className="min-h-0 flex-1 overflow-y-auto bg-surface px-1 py-1">
        {!hasConversation && !loading && (
          <ExamplePrompts
            onSelect={ask}
            disabled={loading}
            clientContext={clientContext}
          />
        )}

        {messages.map((message, index) => (
          <MessageBubble key={`${message.timestamp}-${index}`} message={message} />
        ))}

        {loading && <LoadingState />}
        {error && <p className="mt-2 px-1 text-[0.8125rem] text-danger">{error}</p>}
      </div>

      <QueryInput onSubmit={ask} disabled={loading} />
    </div>
  );
}
