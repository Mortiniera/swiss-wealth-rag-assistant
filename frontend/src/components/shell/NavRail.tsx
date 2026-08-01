import type { ComponentType } from "react";
import { ClientsIcon, PoliciesIcon } from "../ui";
import { NAV_ITEMS, type NavId } from "../../types/workspace";
import { cn } from "../../utils/cn";

type NavRailProps = {
  active: NavId;
  onSelect: (id: NavId) => void;
};

const ICONS: Record<NavId, ComponentType> = {
  clients: ClientsIcon,
  policies: PoliciesIcon,
};

export function NavRail({ active, onSelect }: NavRailProps) {
  return (
    <nav
      className="flex w-14 shrink-0 flex-col gap-1 border-r border-border bg-brand-deep/95 px-1.5 py-3"
      aria-label="Primary"
    >
      {NAV_ITEMS.map((item) => {
        const isActive = item.id === active;
        const Icon = ICONS[item.id];
        return (
          <button
            key={item.id}
            type="button"
            className={cn(
              "relative flex flex-col items-center gap-1 rounded-sm px-1 py-2.5 transition-colors",
              isActive
                ? "bg-white/10 text-white"
                : "text-white/55 hover:bg-white/5 hover:text-white/90",
            )}
            onClick={() => onSelect(item.id)}
            aria-current={isActive ? "page" : undefined}
            title={item.label}
          >
            {isActive && (
              <span
                className="absolute top-2 bottom-2 left-0 w-0.5 rounded-full bg-white"
                aria-hidden="true"
              />
            )}
            <Icon />
            <span className="text-[0.6rem] font-medium tracking-wide">{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
