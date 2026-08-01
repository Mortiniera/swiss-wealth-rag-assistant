import { Modal } from "../ui";

type ExcerptModalProps = {
  open: boolean;
  onClose: () => void;
  title: string;
  fileLabel: string;
  excerpt: string;
};

export function ExcerptModal({
  open,
  onClose,
  title,
  fileLabel,
  excerpt,
}: ExcerptModalProps) {
  return (
    <Modal open={open} onClose={onClose} title={title} subtitle={fileLabel}>
      <pre className="m-0 whitespace-pre-wrap font-sans text-[0.875rem] leading-relaxed text-ink-secondary">
        {excerpt}
      </pre>
    </Modal>
  );
}
