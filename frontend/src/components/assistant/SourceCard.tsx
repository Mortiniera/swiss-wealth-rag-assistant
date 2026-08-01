import { useState } from "react";
import type { Source } from "../../api/client";
import { fileName } from "../../utils/paths";
import {
  displaySourceHeading,
  relevanceClassName,
  relevanceLabel,
} from "../../utils/sourceDisplay";
import { ExcerptModal } from "./ExcerptModal";

type SourceCardProps = {
  source: Source;
  index: number;
  anchorId: string;
  topScore: number;
};

export function SourceCard({ source, index, anchorId, topScore }: SourceCardProps) {
  const [excerptOpen, setExcerptOpen] = useState(false);
  const heading = displaySourceHeading(source);
  const relevance = relevanceLabel(source.score, topScore);
  const excerpt = source.text?.trim();

  return (
    <>
      <article id={anchorId} className="scroll-mt-3 bg-surface-raised px-2.5 py-2 text-left">
        <div className="flex items-start justify-between gap-2">
          <h3 className="m-0 text-[0.8125rem] leading-snug font-semibold text-ink">
            <span className="mr-1 inline-flex h-[1.1rem] min-w-[1.1rem] items-center justify-center rounded-sm bg-accent-soft px-1 align-middle text-[0.68rem] font-semibold tabular-nums text-accent">
              {index}
            </span>
            {heading}
          </h3>
          <span className={`shrink-0 text-[0.6875rem] ${relevanceClassName(source.score, topScore)}`}>
            {relevance}
          </span>
        </div>

        <p className="mt-1 mb-0 font-mono text-[0.6875rem] text-ink-tertiary">
          {fileName(source.source_file)}
        </p>

        {excerpt && (
          <button
            type="button"
            className="mt-1.5 text-[0.75rem] font-medium text-accent hover:underline"
            onClick={() => setExcerptOpen(true)}
          >
            Show excerpt
          </button>
        )}

        <details className="mt-1 text-[0.6875rem] text-ink-tertiary">
          <summary className="cursor-pointer select-none">Technical details</summary>
          <p className="mt-1 mb-0 break-all">File: {source.source_file}</p>
          <p className="mt-0.5 mb-0">Chunk: {source.chunk_id}</p>
          <p className="mt-0.5 mb-0">RRF: {source.score.toFixed(4)}</p>
        </details>
      </article>

      {excerpt && (
        <ExcerptModal
          open={excerptOpen}
          onClose={() => setExcerptOpen(false)}
          title={`[${index}] ${heading}`}
          fileLabel={fileName(source.source_file)}
          excerpt={excerpt}
        />
      )}
    </>
  );
}
