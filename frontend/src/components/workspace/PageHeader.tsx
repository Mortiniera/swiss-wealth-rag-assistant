import type { ReactNode } from "react";

type PageHeaderProps = {
  title: string;
  description: string;
  actions?: ReactNode;
};

export function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div className="min-w-0">
        <h2 className="font-serif text-[1.375rem] leading-tight font-semibold tracking-[-0.02em] text-brand sm:text-[1.5rem]">
          {title}
        </h2>
        <p className="mt-1 max-w-lg text-[0.875rem] text-ink-secondary">{description}</p>
      </div>
      {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
    </div>
  );
}
