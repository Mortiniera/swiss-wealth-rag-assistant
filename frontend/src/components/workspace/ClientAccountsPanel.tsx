import { useState } from "react";
import type { Account, Holding } from "../../api/client";
import {
  formatDate,
  formatLabel,
  formatMoney,
  statusTone,
} from "../../utils/clientDisplay";
import { takePreview } from "../../utils/listPreview";
import { Badge, Modal } from "../ui";
import { EmptyPanelBody, ShowAllFooter } from "./ShowAllFooter";

type ClientAccountsPanelProps = {
  accounts: Account[];
};

function holdingsTotal(holdings: Holding[]): { amount: number; currency: string } | null {
  if (holdings.length === 0) return null;
  const currency = holdings[0]?.currency ?? "CHF";
  const amount = holdings.reduce((sum, row) => sum + Number(row.market_value || 0), 0);
  if (Number.isNaN(amount)) return null;
  return { amount, currency };
}

function HoldingsBlock({ account }: { account: Account }) {
  const holdings = account.holdings ?? [];
  if (holdings.length === 0) {
    return (
      <p className="mt-2 mb-0 text-[0.75rem] text-ink-tertiary">No holdings on file</p>
    );
  }

  const total = holdingsTotal(holdings);
  const base = account.base_currency || total?.currency || account.currency;

  return (
    <div className="mt-2.5 border border-border bg-surface-muted/40 px-2.5 py-2">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="m-0 text-[0.75rem] font-medium text-ink">
          Holdings
          {account.portfolio_name ? (
            <span className="font-normal text-ink-tertiary">
              {" "}
              · {account.portfolio_name}
            </span>
          ) : null}
        </p>
        {total && (
          <p className="m-0 font-mono text-[0.75rem] font-semibold tabular-nums text-ink">
            {formatMoney(total.amount, base)}
          </p>
        )}
      </div>
      {account.portfolio_as_of && (
        <p className="mt-0.5 mb-1.5 text-[0.6875rem] text-ink-tertiary">
          As of {formatDate(account.portfolio_as_of)}
        </p>
      )}
      <ul className="m-0 list-none space-y-1 p-0">
        {holdings.map((row) => (
          <li
            key={`${account.id}-${row.asset_symbol}`}
            className="flex flex-wrap items-baseline justify-between gap-2 text-[0.75rem]"
          >
            <span className="min-w-0 text-ink">
              <span className="font-mono font-medium">{row.asset_symbol}</span>
              <span className="text-ink-tertiary"> · {row.asset_name}</span>
            </span>
            <span className="font-mono tabular-nums text-ink-secondary">
              {formatMoney(row.market_value, row.currency)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function AccountRows({ items }: { items: Account[] }) {
  return (
    <ul className="m-0 list-none divide-y divide-border p-0">
      {items.map((account) => (
        <li key={account.id} className="px-4 py-3">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <p className="m-0 font-mono text-[0.8125rem] font-semibold text-ink">
                  {account.account_code}
                </p>
                <Badge tone={statusTone(account.status)}>
                  {formatLabel(account.status)}
                </Badge>
              </div>
              <p className="mt-0.5 mb-0 text-[0.75rem] text-ink-tertiary">
                {formatLabel(account.account_type)} · {account.currency}
              </p>
            </div>
            <p className="m-0 font-mono text-[0.6875rem] text-ink-tertiary">
              {account.iban_synthetic}
            </p>
          </div>

          {account.restrictions.length > 0 ? (
            <ul className="mt-2.5 mb-0 list-none space-y-1.5 p-0">
              {account.restrictions.map((restriction, index) => (
                <li
                  key={`${account.id}-${restriction.restriction_type}-${index}`}
                  className="border border-[#efd2cd] bg-[#f8e8e6]/40 px-2.5 py-2"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="m-0 text-[0.8125rem] font-medium text-ink">
                      {formatLabel(restriction.restriction_type)}
                    </p>
                    <Badge tone={statusTone(restriction.status)}>
                      {formatLabel(restriction.status)}
                    </Badge>
                  </div>
                  <p className="mt-0.5 mb-0 text-[0.75rem] text-ink-secondary">
                    Reason: {formatLabel(restriction.reason_code)} · From{" "}
                    {formatDate(restriction.effective_from)}
                  </p>
                  {restriction.notes && (
                    <p className="mt-1 mb-0 text-[0.75rem] text-ink-secondary">
                      {restriction.notes}
                    </p>
                  )}
                </li>
              ))}
            </ul>
          ) : account.status.toLowerCase() === "restricted" ? (
            <p className="mt-2 mb-0 text-[0.75rem] text-ink-secondary">
              Account flagged restricted — active restriction details not listed.
            </p>
          ) : (
            <p className="mt-2 mb-0 text-[0.75rem] text-ink-tertiary">No restrictions</p>
          )}

          <HoldingsBlock account={account} />
        </li>
      ))}
    </ul>
  );
}

export function ClientAccountsPanel({ accounts }: ClientAccountsPanelProps) {
  const [showAll, setShowAll] = useState(false);
  const { preview, remaining } = takePreview(accounts);
  const holdingCount = accounts.reduce(
    (sum, account) => sum + (account.holdings?.length ?? 0),
    0,
  );

  return (
    <section className="border border-border bg-surface-raised">
      <header className="flex items-center justify-between gap-2 border-b border-border px-4 py-2.5">
        <h3 className="m-0 text-[0.8125rem] font-semibold text-brand">
          Accounts, restrictions & holdings
        </h3>
        <span className="text-[0.75rem] text-ink-tertiary">
          {accounts.length} account{accounts.length === 1 ? "" : "s"}
          {holdingCount > 0 ? ` · ${holdingCount} holdings` : ""}
        </span>
      </header>

      {accounts.length === 0 ? (
        <EmptyPanelBody>No accounts on file.</EmptyPanelBody>
      ) : (
        <>
          <AccountRows items={preview} />
          <ShowAllFooter
            remaining={remaining}
            noun="account"
            onShowAll={() => setShowAll(true)}
          />
        </>
      )}

      <Modal
        open={showAll}
        onClose={() => setShowAll(false)}
        title="All accounts"
        subtitle={`${accounts.length} accounts`}
        wide
      >
        <div className="-mx-4 -my-3">
          <AccountRows items={accounts} />
        </div>
      </Modal>
    </section>
  );
}
