import { useState } from "react";
import type { ServiceRequest } from "../../api/client";
import {
  formatDate,
  formatLabel,
  isSlaBreached,
  statusTone,
} from "../../utils/clientDisplay";
import { takePreview } from "../../utils/listPreview";
import { Badge, Modal } from "../ui";
import { EmptyPanelBody, ShowAllFooter } from "./ShowAllFooter";

type ClientServiceRequestsPanelProps = {
  requests: ServiceRequest[];
};

function ServiceRequestRows({ items }: { items: ServiceRequest[] }) {
  return (
    <ul className="m-0 list-none divide-y divide-border p-0">
      {items.map((request) => {
        const slaLate = isSlaBreached(request.status, request.sla_due_at);
        return (
          <li key={request.id} className="px-4 py-3">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="m-0 font-mono text-[0.8125rem] font-semibold text-ink">
                    {request.request_code}
                  </p>
                  <Badge tone={statusTone(request.status)}>
                    {formatLabel(request.status)}
                  </Badge>
                  <Badge tone={statusTone(request.priority)}>
                    {formatLabel(request.priority)}
                  </Badge>
                  {slaLate && <Badge tone="danger">SLA</Badge>}
                </div>
                <p className="mt-0.5 mb-0 text-[0.8125rem] text-ink">{request.subject}</p>
                <p className="mt-1 mb-0 text-[0.75rem] text-ink-tertiary">
                  {formatLabel(request.request_type)}
                  {request.assigned_employee_code
                    ? ` · ${request.assigned_employee_code}`
                    : " · Unassigned"}
                </p>
              </div>
              <div className="text-right text-[0.75rem] text-ink-tertiary">
                <p className="m-0">Opened {formatDate(request.opened_at)}</p>
                {request.sla_due_at && (
                  <p className={`mt-0.5 mb-0 ${slaLate ? "font-medium text-danger" : ""}`}>
                    SLA {formatDate(request.sla_due_at)}
                  </p>
                )}
                {request.resolved_at && (
                  <p className="mt-0.5 mb-0">Resolved {formatDate(request.resolved_at)}</p>
                )}
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export function ClientServiceRequestsPanel({
  requests,
}: ClientServiceRequestsPanelProps) {
  const [showAll, setShowAll] = useState(false);
  const openCount = requests.filter((r) => r.status.toLowerCase() === "open").length;
  const breached = requests.filter((r) => isSlaBreached(r.status, r.sla_due_at));
  const openOrLate = requests.filter(
    (r) => r.status.toLowerCase() === "open" || isSlaBreached(r.status, r.sla_due_at),
  );
  const openIds = new Set(openOrLate.map((r) => r.id));
  const previewSource = [...openOrLate, ...requests.filter((r) => !openIds.has(r.id))];
  const { preview, remaining } = takePreview(previewSource);

  return (
    <section className="border border-border bg-surface-raised">
      <header className="flex items-center justify-between gap-2 border-b border-border px-4 py-2.5">
        <h3 className="m-0 text-[0.8125rem] font-semibold text-brand">Service requests</h3>
        <span className="text-[0.75rem] text-ink-tertiary">
          {openCount} open · {requests.length} total
        </span>
      </header>

      {breached.length > 0 && (
        <div className="border-b border-[#efd2cd] bg-[#f8e8e6] px-4 py-2.5 text-[0.8125rem] text-danger">
          <span className="font-semibold">SLA breached</span>
          <span>
            {" "}
            — {breached[0].request_code} due {formatDate(breached[0].sla_due_at)}
          </span>
        </div>
      )}

      {requests.length === 0 ? (
        <EmptyPanelBody>No service requests on file.</EmptyPanelBody>
      ) : (
        <>
          <ServiceRequestRows items={preview} />
          <ShowAllFooter
            remaining={remaining}
            noun="request"
            onShowAll={() => setShowAll(true)}
          />
        </>
      )}

      <Modal
        open={showAll}
        onClose={() => setShowAll(false)}
        title="All service requests"
        subtitle={`${requests.length} requests`}
        wide
      >
        <div className="-mx-4 -my-3">
          <ServiceRequestRows items={requests} />
        </div>
      </Modal>
    </section>
  );
}
