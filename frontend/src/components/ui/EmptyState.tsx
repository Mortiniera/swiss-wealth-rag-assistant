type EmptyStateProps = {
  title: string;
  description: string;
};

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-1 flex-col items-start justify-center px-6 py-12">
      <p className="text-[0.9375rem] font-semibold text-ink">{title}</p>
      <p className="mt-1.5 max-w-md text-[0.875rem] leading-relaxed text-ink-secondary">
        {description}
      </p>
    </div>
  );
}
