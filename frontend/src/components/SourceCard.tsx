import type { Source } from "../api/client";
import {
    displaySourceHeading,
    relevanceClassName,
    relevanceLabel,
} from "../utils/sourceDisplay";

type SourceCardProps = {
    source: Source;
    index: number;
    anchorId: string;
    topScore: number;
};

export function SourceCard({ source, index, anchorId, topScore }: SourceCardProps) {
    const heading = displaySourceHeading(source);
    const relevance = relevanceLabel(source.score, topScore);

    return (
        <article id={anchorId} className="source-card">
            <h3 className="source-card__heading">
                <span className="source-card__index">[{index}]</span> {heading}
            </h3>
            <p className="source-card__file">
                <span className="source-card__meta-label">Source file:</span> {source.source_file}
            </p>
            <p className="source-card__relevance-row">
                <span className="source-card__meta-label">Relevance:</span>{" "}
                <span className={relevanceClassName(source.score, topScore)}>{relevance}</span>
            </p>
            {source.text?.trim() && (
                <blockquote className="source-card__excerpt">{source.text.trim()}</blockquote>
            )}
            <details className="source-card__details">
                <summary>Technical details</summary>
                <p>Chunk ID: {source.chunk_id}</p>
                <p>RRF score: {source.score.toFixed(4)}</p>
            </details>
        </article>
    );
}
