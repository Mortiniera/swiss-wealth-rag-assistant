import type { ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  description?: string;
  breadcrumb?: ReactNode;
  actions?: ReactNode;
  leading?: ReactNode;
};

export function PageHeader({
  title,
  description,
  breadcrumb,
  actions,
  leading,
}: PageHeaderProps) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div className="min-w-0">
        {breadcrumb && <div className="mb-2">{breadcrumb}</div>}
        <div className="flex items-start gap-3">
          {leading}
          <div className="min-w-0">
            <h2 className="font-serif text-[1.375rem] leading-tight font-semibold tracking-[-0.02em] text-brand sm:text-[1.5rem]">
              {title}
            </h2>
            {description && (
              <p className="mt-1 max-w-lg text-[0.875rem] text-ink-secondary">{description}</p>
            )}
          </div>
        </div>
      </div>
      {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
    </div>
  );
}
