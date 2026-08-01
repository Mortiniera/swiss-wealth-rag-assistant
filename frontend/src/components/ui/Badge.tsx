import type { ReactNode } from "react";
import { cn } from "../../utils/cn";

type BadgeTone = "neutral" | "info" | "warning" | "danger" | "success";

type BadgeProps = {
  children: ReactNode;
  tone?: BadgeTone;
  className?: string;
};

const TONE: Record<BadgeTone, string> = {
  neutral: "bg-surface-muted text-ink-secondary",
  info: "bg-accent-soft text-accent",
  warning: "bg-[#f5efd8] text-warn",
  danger: "bg-[#f8e8e6] text-danger",
  success: "bg-[#e7f0ea] text-[#1f6b45]",
};

export function Badge({ children, tone = "info", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-sm px-1.5 py-0.5 text-[0.625rem] font-semibold tracking-wide uppercase",
        TONE[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
