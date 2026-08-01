import type { ReactNode } from "react";
import type { Client } from "../../api/client";
import { formatDate, formatLabel, statusTone } from "../../utils/clientDisplay";
import { Badge } from "../ui";

type ClientProfilePanelProps = {
  client: Client;
};

function Field({
  label,
  value,
  badge,
}: {
  label: string;
  value?: string;
  badge?: ReactNode;
}) {
  return (
    <div>
      <dt className="text-[0.6875rem] font-semibold tracking-[0.04em] text-ink-tertiary uppercase">
        {label}
      </dt>
      <dd className="mt-0.5 mb-0 flex flex-wrap items-center gap-2 text-[0.875rem] text-ink">
        {badge ?? <span>{value ?? "—"}</span>}
      </dd>
    </div>
  );
}

export function ClientProfilePanel({ client }: ClientProfilePanelProps) {
  const kyc = client.kyc_profile;
  const suitability = client.suitability_profile;
  const prefs = client.communication_preference;
  const rm = client.primary_assignment;
  const kycExpired = kyc?.status?.toLowerCase() === "expired";

  return (
    <section className="border border-border bg-surface-raised">
      <header className="border-b border-border px-4 py-2.5">
        <h3 className="m-0 text-[0.8125rem] font-semibold text-brand">Profile & KYC</h3>
      </header>

      {kycExpired && (
        <div className="border-b border-[#efd2cd] bg-[#f8e8e6] px-4 py-2.5 text-[0.8125rem] text-danger">
          <span className="font-semibold">KYC expired</span>
          {kyc?.document_expiry && (
            <span> — document expired {formatDate(kyc.document_expiry)}</span>
          )}
          {kyc?.notes ? <span>. {kyc.notes}</span> : null}
        </div>
      )}

      <dl className="m-0 grid gap-4 px-4 py-4 sm:grid-cols-2">
        <Field label="Client code" value={client.client_code} />
        <Field
          label="Status"
          badge={<Badge tone={statusTone(client.status)}>{formatLabel(client.status)}</Badge>}
        />
        <Field label="Segment" value={formatLabel(client.segment)} />
        <Field label="Residency" value={client.residency_country} />
        <Field label="Email" value={client.email} />
        <Field label="Household" value={client.household_code ?? "—"} />
        <Field
          label="KYC status"
          badge={
            kyc?.status ? (
              <Badge tone={statusTone(kyc.status)}>{formatLabel(kyc.status)}</Badge>
            ) : (
              <span>—</span>
            )
          }
        />
        <Field label="Document" value={formatLabel(kyc?.document_type)} />
        <Field label="Document expiry" value={formatDate(kyc?.document_expiry)} />
        <Field label="Risk profile" value={formatLabel(suitability?.risk_profile)} />
        <Field label="Suitability" value={formatLabel(suitability?.status)} />
        <Field label="Preferred channel" value={formatLabel(prefs?.preferred_channel)} />
        <Field label="Language" value={prefs?.language?.toUpperCase() ?? "—"} />
        <Field
          label="Cross-border OK"
          value={prefs ? (prefs.cross_border_ok ? "Yes" : "No") : "—"}
        />
        <Field label="Relationship manager" value={rm?.full_name ?? "—"} />
        <Field label="RM code" value={rm?.employee_code ?? "—"} />
      </dl>

      {!kycExpired && kyc?.notes && (
        <p className="m-0 border-t border-border px-4 py-3 text-[0.8125rem] text-ink-secondary">
          <span className="font-semibold text-ink">KYC notes: </span>
          {kyc.notes}
        </p>
      )}
    </section>
  );
}
