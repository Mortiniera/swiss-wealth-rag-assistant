export type Source = {
  institution: string;
  document_title: string;
  source_file: string;
  chunk_id: string;
  score: number;
  text: string;
};

export type AskResponse = {
  answer: string;
  sources: Source[];
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
};

export type Restriction = {
  restriction_type: string;
  reason_code: string;
  status: string;
  effective_from: string;
  effective_to: string | null;
  notes: string | null;
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
};
