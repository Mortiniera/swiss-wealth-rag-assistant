/** Client-context helpers for the assistant dock (not access control). */

export type SelectedClientContext = {
  code: string;
  name: string;
};

/** Enrich the wire question without changing the visible chat bubble. */
export function withClientContext(
  question: string,
  client: SelectedClientContext | null,
): string {
  if (!client) return question;
  return `Regarding Helvetia client ${client.code} (${client.name}): ${question}`;
}

export function clientAwarePrompts(client: SelectedClientContext | null): string[] {
  if (!client) {
    return [
      "What does KYC refresh require when an ID expires?",
      "Why might an outbound transfer stay in pending review?",
      "What should an RM do about fragmented transfers?",
      "Which account restrictions exist, and who can lift them?",
    ];
  }
  return [
    "Why is this client's outbound transfer still in pending review?",
    "Does expired KYC explain a transfer hold for this client?",
    "What should I verify before promising a value date?",
    "How should a complaint or service request be handled for this client?",
  ];
}
