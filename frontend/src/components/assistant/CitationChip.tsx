type CitationChipProps = {
  n: number;
  messageId: string;
};

export function CitationChip({ n, messageId }: CitationChipProps) {
  return (
    <a
      href={`#source-${messageId}-${n}`}
      className="mx-0.5 inline-flex h-[1.15rem] min-w-[1.15rem] translate-y-[-0.05em] items-center justify-center rounded-sm bg-accent-soft px-1 align-baseline text-[0.68rem] font-semibold text-accent no-underline hover:bg-brand hover:text-white"
      title={`Go to source ${n}`}
    >
      {n}
    </a>
  );
}
