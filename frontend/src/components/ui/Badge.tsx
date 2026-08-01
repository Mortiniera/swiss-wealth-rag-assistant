import type { ReactNode } from "react";
import { cn } from "../../utils/cn";

type BadgeProps = {
  children: ReactNode;
  className?: string;
};

export function Badge({ children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "rounded-sm bg-accent-soft px-1.5 py-0.5 text-[0.625rem] font-semibold tracking-wide text-accent uppercase",
        className,
      )}
    >
      {children}
    </span>
  );
}
