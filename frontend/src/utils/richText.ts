/**
 * Pure markdown-lite parser for assistant answers.
 * Rendering lives in components/assistant/RichText.tsx.
 */

export type InlineToken =
  | { type: "text"; value: string }
  | { type: "code"; value: string }
  | { type: "bold"; value: string }
  | { type: "italic"; value: string }
  | { type: "citation"; n: number };

export type RichBlock =
  | { type: "paragraph"; lines: InlineToken[][] }
  | { type: "list"; ordered: boolean; items: InlineToken[][] };

const INLINE_TOKEN =
  /(`[^`]+`|\*\*\*[^*]+\*\*\*|\*\*[^*]+\*\*|__[^_]+__|_[^_]+_|\*[^*]+\*|\[\d+\])/g;

function isBulletLine(line: string): boolean {
  return /^\s*[-*•]\s+/.test(line);
}

function isNumberedLine(line: string): boolean {
  return /^\s*\d+\.\s+/.test(line);
}

function stripListMarker(line: string): string {
  return line.replace(/^\s*(?:[-*•]|\d+\.)\s+/, "");
}

export function tokenizeInline(text: string, sourceCount: number): InlineToken[] {
  const tokens: InlineToken[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  INLINE_TOKEN.lastIndex = 0;
  while ((match = INLINE_TOKEN.exec(text)) !== null) {
    if (match.index > lastIndex) {
      tokens.push({ type: "text", value: text.slice(lastIndex, match.index) });
    }

    const token = match[0];

    if (token.startsWith("`") && token.endsWith("`")) {
      tokens.push({ type: "code", value: token.slice(1, -1) });
    } else if (
      (token.startsWith("***") && token.endsWith("***")) ||
      (token.startsWith("**") && token.endsWith("**")) ||
      (token.startsWith("__") && token.endsWith("__"))
    ) {
      const value = token.startsWith("***") ? token.slice(3, -3) : token.slice(2, -2);
      tokens.push({ type: "bold", value });
    } else if (
      (token.startsWith("*") && token.endsWith("*")) ||
      (token.startsWith("_") && token.endsWith("_"))
    ) {
      tokens.push({ type: "italic", value: token.slice(1, -1) });
    } else {
      const cite = token.match(/^\[(\d+)\]$/);
      if (cite) {
        const n = Number.parseInt(cite[1], 10);
        if (n >= 1 && n <= sourceCount) {
          tokens.push({ type: "citation", n });
        } else {
          tokens.push({ type: "text", value: token });
        }
      } else {
        tokens.push({ type: "text", value: token });
      }
    }

    lastIndex = match.index + token.length;
  }

  if (lastIndex < text.length) {
    tokens.push({ type: "text", value: text.slice(lastIndex) });
  }

  return tokens;
}

export function parseRichText(content: string, sourceCount = 0): RichBlock[] {
  const chunks = content.split(/\n\n+/).filter((block) => block.trim().length > 0);

  return chunks.map((block) => {
    const lines = block.split("\n");
    const allBullets = lines.every(isBulletLine);
    const allNumbered = lines.every(isNumberedLine);

    if ((allBullets || allNumbered) && lines.length > 0) {
      return {
        type: "list" as const,
        ordered: allNumbered,
        items: lines.map((line) => tokenizeInline(stripListMarker(line), sourceCount)),
      };
    }

    return {
      type: "paragraph" as const,
      lines: lines.map((line) => tokenizeInline(line, sourceCount)),
    };
  });
}
