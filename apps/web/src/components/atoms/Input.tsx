/**
 * Input Atom
 *
 * Basic text input component (Stateless).
 */

interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  testId?: string;
}

export const Input = ({
  value,
  onChange,
  placeholder,
  disabled = false,
  testId,
}: InputProps) => {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => {
        onChange(e.target.value);
      }}
      placeholder={placeholder}
      disabled={disabled}
      className="disabled:opacity-ash w-full rounded-card border border-ash-500 bg-night-800 px-4 py-2 text-smoke-100 placeholder:text-ash-500 focus:shadow-glow-sm focus:outline-none disabled:cursor-not-allowed"
      data-testid={testId}
    />
  );
};
