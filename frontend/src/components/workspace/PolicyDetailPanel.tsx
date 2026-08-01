import type { PolicyDetail } from "../../api/client";
import { formatDate, formatLabel, statusTone } from "../../utils/clientDisplay";
import { RichText } from "../assistant/RichText";
import { Badge } from "../ui";

type PolicyDetailPanelProps = {
  policy: PolicyDetail;
};

type DocSection = {
  heading: string | null;
  level: 2 | 3 | null;
  body: string;
};

/** Strip a leading H1 that duplicates the catalog title. */
function stripTitleHeading(body: string, title: string): string {
  const trimmed = body.trim();
  const h1 = trimmed.match(/^#\s+(.+)\n*/);
  if (h1 && h1[1].trim().toLowerCase() === title.trim().toLowerCase()) {
    return trimmed.slice(h1[0].length).trim();
  }
  return trimmed;
}

/** Split markdown into ## / ### sections for a readable ops document view. */
function splitPolicySections(body: string): DocSection[] {
  const text = body.trim();
  if (!text) return [];

  const parts = text.split(/(?=^#{2,3}\s)/m).filter((part) => part.trim().length > 0);
  return parts.map((part) => {
    const headingMatch = part.match(/^(#{2,3})\s+(.+?)(?:\n|$)/);
    if (!headingMatch) {
      return { heading: null, level: null, body: part.trim() };
    }
    const level = headingMatch[1].length === 2 ? 2 : 3;
    const heading = headingMatch[2].trim();
    const rest = part.slice(headingMatch[0].length).trim();
    return { heading, level: level as 2 | 3, body: rest };
  });
}

export function PolicyDetailPanel({ policy }: PolicyDetailPanelProps) {
  const sections = splitPolicySections(stripTitleHeading(policy.body, policy.title));
  const metaBits = [
    formatLabel(policy.category),
    policy.department,
    `Effective ${formatDate(policy.effective_date)}`,
    `v${policy.version}`,
    policy.jurisdiction,
  ];

  return (
    <div className="flex flex-col gap-4">
      <section className="border border-border bg-surface-raised px-4 py-3">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone={statusTone(policy.status)}>{formatLabel(policy.status)}</Badge>
          <Badge tone="neutral">{formatLabel(policy.doc_type)}</Badge>
          <Badge tone="neutral">{formatLabel(policy.confidentiality)}</Badge>
          <span className="text-[0.8125rem] text-ink-secondary">{metaBits.join(" · ")}</span>
        </div>
        {policy.allowed_roles.length > 0 && (
          <p className="mt-2 mb-0 text-[0.75rem] text-ink-tertiary">
            Audience: {policy.allowed_roles.map(formatLabel).join(" · ")}
            {policy.supersedes_document_id
              ? ` · Supersedes ${policy.supersedes_document_id}`
              : ""}
          </p>
        )}
      </section>

      <section className="border border-border bg-surface-raised">
        <header className="border-b border-border px-4 py-2.5">
          <h3 className="m-0 text-[0.8125rem] font-semibold text-brand">Policy text</h3>
        </header>
        <div className="px-4 py-5 sm:px-5">
          {sections.length === 0 ? (
            <p className="m-0 text-[0.875rem] text-ink-secondary">No policy body available.</p>
          ) : (
            <div className="max-w-3xl space-y-5">
              {sections.map((section, index) => (
                <div key={`${section.heading ?? "intro"}-${index}`}>
                  {section.heading && section.level === 2 && (
                    <h4 className="mt-0 mb-2 font-serif text-[1.05rem] font-semibold tracking-[-0.01em] text-brand">
                      {section.heading}
                    </h4>
                  )}
                  {section.heading && section.level === 3 && (
                    <h5 className="mt-0 mb-1.5 text-[0.875rem] font-semibold text-ink">
                      {section.heading}
                    </h5>
                  )}
                  {section.body ? (
                    <RichText
                      content={section.body}
                      messageId={`policy-${policy.document_id}-${index}`}
                      sourceCount={0}
                    />
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
