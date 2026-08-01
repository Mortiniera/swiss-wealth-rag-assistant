import type { Source } from "../../api/client";
import { SourceCard } from "./SourceCard";

type MessageSourcesProps = {
  sources: Source[];
  messageId: string;
};

export function MessageSources({ sources, messageId }: MessageSourcesProps) {
  const topScore = Math.max(...sources.map((item) => item.score), 0);

  return (
    <div className="mt-3 w-full border-t border-border pt-2.5">
      <p className="mb-2 text-[0.6875rem] font-semibold tracking-[0.05em] text-ink-tertiary uppercase">
        Sources
      </p>
      <ol className="m-0 grid list-none gap-1.5 p-0">
        {sources.map((source, index) => (
          <li key={source.chunk_id} className="m-0">
            <SourceCard
              source={source}
              index={index + 1}
              anchorId={`source-${messageId}-${index + 1}`}
              topScore={topScore}
            />
          </li>
        ))}
      </ol>
    </div>
  );
}
