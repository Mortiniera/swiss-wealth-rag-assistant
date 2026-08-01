import { useState } from "react";
import type { Interaction } from "../../api/client";
import { formatDateTime, formatLabel, statusTone } from "../../utils/clientDisplay";
import { takePreview } from "../../utils/listPreview";
import { Badge, Modal } from "../ui";
import { EmptyPanelBody, ShowAllFooter } from "./ShowAllFooter";

type ClientInteractionsPanelProps = {
  interactions: Interaction[];
};

function InteractionRows({ items }: { items: Interaction[] }) {
  return (
    <ul className="m-0 list-none divide-y divide-border p-0">
      {items.map((row) => (
        <li key={row.id} className="px-4 py-3">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <p className="m-0 text-[0.8125rem] font-semibold text-ink">{row.subject}</p>
                <Badge tone={statusTone(row.status)}>{formatLabel(row.status)}</Badge>
              </div>
              <p className="mt-0.5 mb-0 text-[0.8125rem] text-ink-secondary">{row.summary}</p>
              <p className="mt-1 mb-0 text-[0.75rem] text-ink-tertiary">
                {formatLabel(row.channel)} · {formatLabel(row.direction)}
                {row.employee_code ? ` · ${row.employee_code}` : ""}
                {row.related_request_code ? ` · ${row.related_request_code}` : ""}
              </p>
            </div>
            <p className="m-0 shrink-0 text-[0.75rem] text-ink-tertiary">
              {formatDateTime(row.occurred_at)}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}

export function ClientInteractionsPanel({
  interactions,
}: ClientInteractionsPanelProps) {
  const [showAll, setShowAll] = useState(false);
  const { preview, remaining } = takePreview(interactions);

  return (
    <section className="border border-border bg-surface-raised">
      <header className="flex items-center justify-between gap-2 border-b border-border px-4 py-2.5">
        <h3 className="m-0 text-[0.8125rem] font-semibold text-brand">Interactions</h3>
        <span className="text-[0.75rem] text-ink-tertiary">
          {interactions.length} logged
        </span>
      </header>

      {interactions.length === 0 ? (
        <EmptyPanelBody>No interactions on file.</EmptyPanelBody>
      ) : (
        <>
          <InteractionRows items={preview} />
          <ShowAllFooter
            remaining={remaining}
            noun="interaction"
            onShowAll={() => setShowAll(true)}
          />
        </>
      )}

      <Modal
        open={showAll}
        onClose={() => setShowAll(false)}
        title="All interactions"
        subtitle={`${interactions.length} logged`}
        wide
      >
        <div className="-mx-4 -my-3">
          <InteractionRows items={interactions} />
        </div>
      </Modal>
    </section>
  );
}
