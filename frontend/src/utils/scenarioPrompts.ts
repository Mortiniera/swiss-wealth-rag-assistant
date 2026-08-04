/** Pre-built operator prompts for curated CLI-SCEN-* demo clients. */

export type ScenarioPromptPack = {
  title: string;
  prompts: string[];
};

/**
 * Questions are short and keyword-friendly for tool selection.
 * ``withClientContext`` adds the CLI code on the wire; do not prefix it here.
 */
export const SCENARIO_PROMPT_PACKS: Record<string, ScenarioPromptPack> = {
  "CLI-SCEN-01": {
    title: "Expired KYC + stuck transfer",
    prompts: [
      "Why is this client's outbound transfer still in pending review?",
      "Does expired KYC explain the transfer hold and account restriction?",
      "What open KYC refresh service request or interaction is on file?",
      "What should I verify before promising a value date?",
    ],
  },
  "CLI-SCEN-02": {
    title: "Account restriction",
    prompts: [
      "What active account restrictions are on file for this client?",
      "Why is the account marked restricted or under compliance block?",
      "Is there an open compliance review service request?",
      "Who should review lifting this restriction?",
    ],
  },
  "CLI-SCEN-03": {
    title: "Delayed transfer (ops)",
    prompts: [
      "Why is this outbound transfer still pending ops review?",
      "Is KYC valid, or is something else delaying the payment?",
      "What open payment-ops service request or client chase note exists?",
      "What should I tell the client about the delay reason?",
    ],
  },
  "CLI-SCEN-04": {
    title: "Unusual transaction",
    prompts: [
      "Which recent transactions are flagged unusual for this client?",
      "Is there an open AML or unusual-movement review request?",
      "What should I verify before explaining this cash movement?",
      "Does policy require enhanced review for unusual patterns?",
    ],
  },
  "CLI-SCEN-05": {
    title: "Incomplete onboarding",
    prompts: [
      "Is this client's onboarding and KYC package complete?",
      "Is suitability missing or incomplete for this client?",
      "What profile gaps block treating this as a live mandate?",
      "What should an RM complete before investment activity?",
    ],
  },
  "CLI-SCEN-06": {
    title: "Unresolved complaint",
    prompts: [
      "What open complaint or service request is on file?",
      "Summarize the interaction history on the fee dispute.",
      "Is the complaint still within SLA?",
      "How should a complaint ticket be handled for this client?",
    ],
  },
  "CLI-SCEN-07": {
    title: "Missing suitability",
    prompts: [
      "Is the suitability questionnaire missing for this client?",
      "Is KYC valid while suitability is still incomplete?",
      "What profile gaps should the RM chase next?",
      "What does policy require before advisory conversations?",
    ],
  },
  "CLI-SCEN-08": {
    title: "Cross-border communication",
    prompts: [
      "Can we contact this client across the border?",
      "What communication preferences and residency constraints apply?",
      "Is there a logged note about cross-border contact being declined?",
      "What should I check before an outbound email or call?",
    ],
  },
  "CLI-SCEN-09": {
    title: "Dormant relationship",
    prompts: [
      "Why is this relationship marked dormant?",
      "Are suitability or KYC records outdated for this dormant client?",
      "What holdings remain on the custody account?",
      "What should an RM review before reactivating contact?",
    ],
  },
  "CLI-SCEN-10": {
    title: "Portfolio enquiry",
    prompts: [
      "What holdings and market values are on file for this portfolio?",
      "Is there an open enquiry about portfolio performance?",
      "Summarize the client interaction about the portfolio decline.",
      "What can I say without inventing performance attribution?",
    ],
  },
  "CLI-SCEN-11": {
    title: "Channel preference conflict",
    prompts: [
      "What is this client's preferred communication channel?",
      "Does the open follow-up request conflict with that preference?",
      "What interaction notes the channel conflict?",
      "How should ops contact the client without breaking preferences?",
    ],
  },
  "CLI-SCEN-12": {
    title: "Unresolved inbound email",
    prompts: [
      "Is there an inbound email still awaiting reply?",
      "What open service request is linked to the unanswered message?",
      "Summarize the interaction history for this complaint thread.",
      "What should I do before promising a written reply?",
    ],
  },
  "CLI-SCEN-13": {
    title: "High-value cash movement",
    prompts: [
      "What high-value or unusual cash transfers are on file?",
      "Is there an open high-value review service request?",
      "Summarize the RM note on the large booked transfer.",
      "What review steps does policy expect for large cash movements?",
    ],
  },
  "CLI-SCEN-14": {
    title: "Failed document upload",
    prompts: [
      "Why is KYC marked invalid for this client?",
      "Is there an open ticket about the failed identity document upload?",
      "What interaction notes were logged about the upload failure?",
      "What should the client do next to refresh KYC documents?",
    ],
  },
  "CLI-SCEN-15": {
    title: "SLA breach",
    prompts: [
      "Which open service request is past its SLA due date?",
      "Summarize the escalation interaction on the overdue complaint.",
      "What priority and subject are on the breached ticket?",
      "How should an RM handle an SLA-breached service request?",
    ],
  },
};

export function scenarioPromptPack(
  clientCode: string | null | undefined,
): ScenarioPromptPack | null {
  if (!clientCode) return null;
  return SCENARIO_PROMPT_PACKS[clientCode] ?? null;
}
