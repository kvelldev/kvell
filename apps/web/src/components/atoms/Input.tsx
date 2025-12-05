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
      className="w-full px-4 py-2 bg-night-800 border border-ash-500 rounded-card text-smoke-100 placeholder-ash-500 focus:outline-none focus:shadow-glow-sm disabled:opacity-ash disabled:cursor-not-allowed"
      data-testid={testId}
    />
  );
};
