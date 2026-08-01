import type { ButtonHTMLAttributes } from "react";
import { cn } from "../../utils/cn";

type ButtonVariant = "primary" | "soft" | "ghost" | "outline";
type ButtonSize = "sm" | "md";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: ButtonSize;
};

const VARIANT: Record<ButtonVariant, string> = {
  primary:
    "border border-brand bg-brand text-white hover:border-brand-deep hover:bg-brand-deep disabled:opacity-55",
  soft: "border border-border bg-accent-soft text-brand hover:border-border-strong",
  ghost: "border border-transparent text-ink-tertiary hover:bg-surface-muted hover:text-ink",
  outline:
    "border border-border-strong bg-surface-raised text-brand hover:border-accent hover:bg-surface-muted",
};

const SIZE: Record<ButtonSize, string> = {
  sm: "px-2 py-1 text-[0.75rem]",
  md: "px-2.5 py-1.5 text-[0.8125rem]",
};

export function Button({
  variant = "primary",
  size = "md",
  className,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "inline-flex items-center justify-center gap-1.5 rounded-sm font-medium transition-colors disabled:cursor-not-allowed",
        VARIANT[variant],
        SIZE[size],
        className,
      )}
      {...props}
    />
  );
}
