import type { Source } from "../api/client";

type SourceCardProps = {
    source: Source;
};

export function SourceCard({ source }: SourceCardProps) {
    return (
        <article className="source-card">
            <p className="source-card__institution">{source.institution}</p>
            <p className="source-card__title">{source.document_title}</p>
            <p className="source-card__file">{source.source_file}</p>
            <p className="source-card__score">Score: {source.score.toFixed(4)}</p>
        </article>
    );
}