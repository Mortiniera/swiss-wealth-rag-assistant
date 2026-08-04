/** Client-context helpers for the assistant dock (not access control). */

import { scenarioPromptPack } from "./scenarioPrompts";

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

const GENERIC_POLICY_PROMPTS = [
  "What does KYC refresh require when an ID expires?",
  "Why might an outbound transfer stay in pending review?",
  "What should an RM do about fragmented transfers?",
  "Which account restrictions exist, and who can lift them?",
];

const GENERIC_CLIENT_PROMPTS = [
  "Are there any pending or unusual outbound transfers on file?",
  "What KYC or suitability gaps should I be aware of for this client?",
  "What open service requests or interactions are on file?",
  "What account holdings or restrictions should I verify?",
];

export function clientAwarePrompts(client: SelectedClientContext | null): string[] {
  if (!client) {
    return GENERIC_POLICY_PROMPTS;
  }
  const pack = scenarioPromptPack(client.code);
  if (pack) {
    return pack.prompts;
  }
  return GENERIC_CLIENT_PROMPTS;
}

export function clientAwarePromptTitle(
  client: SelectedClientContext | null,
): string | null {
  if (!client) return null;
  return scenarioPromptPack(client.code)?.title ?? null;
}
