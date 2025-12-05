/**
 * Textarea Atom
 *
 * Basic textarea component for multi-line text input (Stateless).
 */

interface TextareaProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  maxLength?: number;
  testId?: string;
}

export const Textarea = ({
  value,
  onChange,
  placeholder,
  disabled = false,
  maxLength,
  testId,
}: TextareaProps) => {
  const baseClasses =
    "w-full px-4 py-3 bg-night-800 text-smoke-100 rounded-card resize-none focus:outline-none focus:shadow-glow-sm transition-all disabled:opacity-ash disabled:cursor-not-allowed font-base font-light";

  return (
    <textarea
      value={value}
      onChange={(event) => {
        onChange(event.target.value);
      }}
      placeholder={placeholder}
      disabled={disabled}
      maxLength={maxLength}
      className={baseClasses}
      rows={6}
      data-testid={testId}
    />
  );
};
