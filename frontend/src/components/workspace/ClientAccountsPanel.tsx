import type { Account } from "../../api/client";
import { formatDate, formatLabel, statusTone } from "../../utils/clientDisplay";
import { Badge } from "../ui";

type ClientAccountsPanelProps = {
  accounts: Account[];
};

export function ClientAccountsPanel({ accounts }: ClientAccountsPanelProps) {
  return (
    <section className="border border-border bg-surface-raised">
      <header className="flex items-center justify-between gap-2 border-b border-border px-4 py-2.5">
        <h3 className="m-0 text-[0.8125rem] font-semibold text-brand">
          Accounts & restrictions
        </h3>
        <span className="text-[0.75rem] text-ink-tertiary">
          {accounts.length} account{accounts.length === 1 ? "" : "s"}
        </span>
      </header>

      {accounts.length === 0 ? (
        <p className="m-0 px-4 py-6 text-[0.875rem] text-ink-secondary">No accounts on file.</p>
      ) : (
        <ul className="m-0 list-none divide-y divide-border p-0">
          {accounts.map((account) => (
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
              ) : (
                <p className="mt-2 mb-0 text-[0.75rem] text-ink-tertiary">No restrictions</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
