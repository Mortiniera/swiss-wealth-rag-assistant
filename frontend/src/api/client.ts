/** Compatibility barrel — prefer named imports from `./ask`, `./banking`, or `./index`. */
export { askQuestion } from "./ask";
export {
  getClient,
  getClientAccounts,
  getClientInteractions,
  getClientServiceRequests,
  getClientTransactions,
  listClients,
} from "./banking";
export { ApiError } from "./errors";
export type {
  Account,
  AskResponse,
  ChatMessage,
  Client,
  CommunicationPreference,
  Interaction,
  KYCProfile,
  PrimaryAssignment,
  Restriction,
  ServiceRequest,
  Source,
  SuitabilityProfile,
  Transaction,
} from "./types";
