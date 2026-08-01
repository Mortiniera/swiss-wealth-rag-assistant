import { useState } from "react";
import type { Transaction } from "../../api/client";
import {
  formatDate,
  formatDateTime,
  formatLabel,
  formatMoney,
  statusTone,
} from "../../utils/clientDisplay";
import { takePreview } from "../../utils/listPreview";
import { Badge, Modal } from "../ui";
import { EmptyPanelBody, ShowAllFooter } from "./ShowAllFooter";

type ClientTransactionsPanelProps = {
  transactions: Transaction[];
};

function isHeld(txn: Transaction): boolean {
  const status = txn.status.toLowerCase();
  return status === "pending" || status === "pending_review" || Boolean(txn.delay_reason_code);
}

function TransactionRows({ items }: { items: Transaction[] }) {
  return (
    <ul className="m-0 list-none divide-y divide-border p-0">
      {items.map((txn) => {
        const delayed = Boolean(txn.delay_reason_code);
        return (
          <li
            key={txn.id}
            className={
              delayed
                ? "border-l-2 border-l-danger bg-[#f8e8e6]/25 px-4 py-3"
                : "px-4 py-3"
            }
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="m-0 font-mono text-[0.8125rem] font-semibold text-ink">
                    {txn.transaction_code}
                  </p>
                  <Badge tone={statusTone(txn.status)}>{formatLabel(txn.status)}</Badge>
                  {txn.is_unusual && <Badge tone="warning">Unusual</Badge>}
                </div>
                <p className="mt-0.5 mb-0 text-[0.8125rem] text-ink">{txn.description}</p>
                <p className="mt-1 mb-0 text-[0.75rem] text-ink-tertiary">
                  {formatLabel(txn.txn_type)} · {txn.account_code}
                  {txn.counterparty_name ? ` · ${txn.counterparty_name}` : ""}
                </p>
                {delayed && (
                  <p className="mt-1.5 mb-0 text-[0.75rem] font-medium text-danger">
                    Delay: {formatLabel(txn.delay_reason_code)}
                  </p>
                )}
              </div>
              <div className="text-right">
                <p className="m-0 font-mono text-[0.875rem] font-semibold tabular-nums text-ink">
                  {formatMoney(txn.amount, txn.currency)}
                </p>
                <p className="mt-0.5 mb-0 text-[0.6875rem] text-ink-tertiary">
                  {txn.booked_at
                    ? `Booked ${formatDate(txn.booked_at)}`
                    : `Created ${formatDateTime(txn.created_at)}`}
                </p>
              </div>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export function ClientTransactionsPanel({
  transactions,
}: ClientTransactionsPanelProps) {
  const [showAll, setShowAll] = useState(false);
  const held = transactions.filter(isHeld);
  // Surface held transfers in the short preview, then fill with newest remaining.
  const previewSource = [
    ...held,
    ...transactions.filter((txn) => !isHeld(txn)),
  ];
  const { preview, remaining } = takePreview(previewSource);

  return (
    <section className="border border-border bg-surface-raised">
      <header className="flex items-center justify-between gap-2 border-b border-border px-4 py-2.5">
        <h3 className="m-0 text-[0.8125rem] font-semibold text-brand">Transactions</h3>
        <span className="text-[0.75rem] text-ink-tertiary">
          {transactions.length} movement{transactions.length === 1 ? "" : "s"}
        </span>
      </header>

      {held.length > 0 && (
        <div className="border-b border-[#efd2cd] bg-[#f8e8e6] px-4 py-2.5 text-[0.8125rem] text-danger">
          <span className="font-semibold">
            {held.length} transfer{held.length === 1 ? "" : "s"} held
          </span>
          {held[0]?.delay_reason_code && (
            <span>
              {" "}
              — {held[0].transaction_code}: {formatLabel(held[0].delay_reason_code)}
            </span>
          )}
        </div>
      )}

      {transactions.length === 0 ? (
        <EmptyPanelBody>No transactions on file.</EmptyPanelBody>
      ) : (
        <>
          <TransactionRows items={preview} />
          <ShowAllFooter
            remaining={remaining}
            noun="movement"
            onShowAll={() => setShowAll(true)}
          />
        </>
      )}

      <Modal
        open={showAll}
        onClose={() => setShowAll(false)}
        title="All transactions"
        subtitle={`${transactions.length} movements`}
        wide
      >
        <div className="-mx-4 -my-3">
          <TransactionRows items={transactions} />
        </div>
      </Modal>
    </section>
  );
}
