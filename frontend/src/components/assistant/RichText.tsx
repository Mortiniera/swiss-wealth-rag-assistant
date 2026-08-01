import type { ReactNode } from "react";
import { parseRichText, type InlineToken } from "../../utils/richText";
import { CitationChip } from "./CitationChip";

type RichTextProps = {
  content: string;
  messageId: string;
  sourceCount?: number;
};

function renderInline(tokens: InlineToken[], messageId: string, keyPrefix: string): ReactNode[] {
  return tokens.map((token, index) => {
    const key = `${messageId}-${keyPrefix}-${index}`;
    switch (token.type) {
      case "text":
        return <span key={key}>{token.value}</span>;
      case "code":
        return (
          <code
            key={key}
            className="rounded-sm bg-accent-soft px-1 py-0.5 font-mono text-[0.8em] font-medium text-brand"
          >
            {token.value}
          </code>
        );
      case "bold":
        return (
          <strong key={key} className="font-semibold text-ink">
            {token.value}
          </strong>
        );
      case "italic":
        return (
          <em key={key} className="italic text-ink">
            {token.value}
          </em>
        );
      case "citation":
        return <CitationChip key={key} n={token.n} messageId={messageId} />;
      default:
        return null;
    }
  });
}

export function RichText({ content, messageId, sourceCount = 0 }: RichTextProps) {
  const blocks = parseRichText(content, sourceCount);

  return (
    <>
      {blocks.map((block, blockIndex) => {
        if (block.type === "list") {
          const ListTag = block.ordered ? "ol" : "ul";
          return (
            <ListTag
              key={`${messageId}-block-${blockIndex}`}
              className={`m-0 ${blockIndex > 0 ? "mt-2.5" : ""} list-outside space-y-1 pl-4 text-[0.8375rem] leading-[1.55] text-ink ${block.ordered ? "list-decimal" : "list-disc"}`}
            >
              {block.items.map((item, itemIndex) => (
                <li key={`${messageId}-li-${blockIndex}-${itemIndex}`} className="pl-0.5">
                  {renderInline(item, messageId, `b${blockIndex}i${itemIndex}`)}
                </li>
              ))}
            </ListTag>
          );
        }

        return (
          <p
            key={`${messageId}-block-${blockIndex}`}
            className={`m-0 text-[0.8375rem] leading-[1.55] text-ink${blockIndex > 0 ? " mt-2.5" : ""}`}
          >
            {block.lines.map((line, lineIndex) => (
              <span key={`${messageId}-line-${blockIndex}-${lineIndex}`}>
                {lineIndex > 0 && <br />}
                {renderInline(line, messageId, `b${blockIndex}r${lineIndex}`)}
              </span>
            ))}
          </p>
        );
      })}
    </>
  );
}
