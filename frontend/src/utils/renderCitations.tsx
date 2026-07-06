import type { ReactNode } from "react";

const CITATION_PATTERN = /(\[\d+\])/g;

export function renderTextWithCitations(
    text: string,
    messageId: string,
    sourceCount: number,
): ReactNode[] {
    return text.split(CITATION_PATTERN).map((part, index) => {
        const match = part.match(/^\[(\d+)\]$/);
        if (!match) {
            return part;
        }

        const citationNumber = Number.parseInt(match[1], 10);
        if (citationNumber < 1 || citationNumber > sourceCount) {
            return part;
        }

        return (
            <a
                key={`${messageId}-citation-${index}`}
                href={`#source-${messageId}-${citationNumber}`}
                className="citation-ref"
            >
                [{citationNumber}]
            </a>
        );
    });
}
