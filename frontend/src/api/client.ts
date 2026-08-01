/** Compatibility barrel — prefer named imports from `./ask`, `./banking`, `./policies`, or `./index`. */
export { askQuestion } from "./ask";
export {
  getClient,
  getClientAccounts,
  getClientInteractions,
  getClientServiceRequests,
  getClientTransactions,
  listClients,
} from "./banking";
export { getPolicy, listPolicies } from "./policies";
export { ApiError } from "./errors";
export type {
  Account,
  AskResponse,
  ChatMessage,
  Client,
  CommunicationPreference,
  Interaction,
  KYCProfile,
  PolicyDetail,
  PolicySummary,
  PrimaryAssignment,
  Restriction,
  ServiceRequest,
  Source,
  SuitabilityProfile,
  Transaction,
} from "./types";
