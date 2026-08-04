export type Source = {
  institution: string;
  document_title: string;
  source_file: string;
  chunk_id: string;
  score: number;
  text: string;
};

export type EvidenceItem = {
  label: string;
  value: string;
  source:
    | "client_profile"
    | "account_summary"
    | "account_restrictions"
    | "recent_transactions"
    | "open_service_requests"
    | "interaction_history";
};

export type AskResponse = {
  answer: string;
  sources: Source[];
  evidence?: EvidenceItem[];
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type KYCProfile = {
  status: string;
  document_type: string;
  document_expiry: string;
  last_reviewed_at: string | null;
  notes: string | null;
};

export type SuitabilityProfile = {
  status: string;
  risk_profile: string | null;
  completed_at: string | null;
};

export type CommunicationPreference = {
  preferred_channel: string;
  marketing_opt_in: boolean;
  cross_border_ok: boolean;
  language: string;
};

export type PrimaryAssignment = {
  employee_code: string;
  full_name: string;
  email: string;
};

export type Client = {
  id: string;
  client_code: string;
  full_name: string;
  email: string;
  residency_country: string;
  status: string;
  segment: string;
  household_code: string | null;
  created_at: string;
  kyc_profile: KYCProfile | null;
  suitability_profile: SuitabilityProfile | null;
  communication_preference: CommunicationPreference | null;
  primary_assignment: PrimaryAssignment | null;
  /** Priority-ordered directory signals from the API. */
  open_items?: string[];
};

export type Restriction = {
  restriction_type: string;
  reason_code: string;
  status: string;
  effective_from: string;
  effective_to: string | null;
  notes: string | null;
};

export type Holding = {
  asset_symbol: string;
  asset_name: string;
  quantity: string;
  market_value: string;
  currency: string;
};

export type Account = {
  id: string;
  account_code: string;
  account_type: string;
  currency: string;
  status: string;
  iban_synthetic: string;
  opened_at: string;
  restrictions: Restriction[];
  portfolio_name?: string | null;
  portfolio_as_of?: string | null;
  base_currency?: string | null;
  holdings?: Holding[];
};

export type Transaction = {
  id: string;
  transaction_code: string;
  account_code: string;
  txn_type: string;
  amount: string;
  currency: string;
  status: string;
  booked_at: string | null;
  value_date: string | null;
  counterparty_name: string | null;
  description: string;
  delay_reason_code: string | null;
  is_unusual: boolean;
  created_at: string;
};

export type Interaction = {
  id: string;
  channel: string;
  direction: string;
  subject: string;
  summary: string;
  occurred_at: string;
  status: string;
  employee_code: string | null;
  related_request_code: string | null;
};

export type ServiceRequest = {
  id: string;
  request_code: string;
  request_type: string;
  status: string;
  priority: string;
  subject: string;
  opened_at: string;
  sla_due_at: string | null;
  resolved_at: string | null;
  assigned_employee_code: string | null;
};

export type PolicySummary = {
  id: string;
  document_id: string;
  title: string;
  department: string;
  doc_type: string;
  category: string;
  jurisdiction: string;
  allowed_roles: string[];
  effective_date: string;
  version: string;
  status: string;
  confidentiality: string;
  supersedes_document_id: string | null;
  source_path: string;
  updated_at: string;
};

export type PolicyDetail = PolicySummary & {
  body: string;
};

export type Actor = {
  employee_code: string;
  full_name: string;
  email: string;
  role_code: string;
  role_name: string;
};

export type ClientPanelId =
  | "profile"
  | "accounts"
  | "transactions"
  | "service_requests"
  | "interactions";

export type PanelLayout = {
  focus_hint: string;
  primary: ClientPanelId[];
  secondary: ClientPanelId[];
};

export type WorkspaceContext = {
  actor: Actor;
  client_scope: "assigned" | "all";
  panel_layout: PanelLayout;
  note: string;
};
