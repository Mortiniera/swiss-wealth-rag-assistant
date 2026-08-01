import { PERSONAS, type PersonaId } from "../../types/workspace";

type PersonaSelectProps = {
  value: PersonaId;
  onChange: (persona: PersonaId) => void;
};

export function PersonaSelect({ value, onChange }: PersonaSelectProps) {
  return (
    <label className="flex items-center gap-2">
      <span className="sr-only">Operator persona</span>
      <select
        className="max-w-[12.5rem] rounded-sm border border-border bg-surface-raised py-1.5 pr-7 pl-2.5 text-[0.8125rem] text-ink"
        value={value}
        onChange={(event) => onChange(event.target.value as PersonaId)}
        aria-label="Operator persona"
      >
        {PERSONAS.map((persona) => (
          <option key={persona.id} value={persona.id}>
            {persona.label}
          </option>
        ))}
      </select>
    </label>
  );
}
