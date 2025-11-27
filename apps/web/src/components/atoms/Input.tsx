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
}

export const Input = ({
  value,
  onChange,
  placeholder,
  disabled = false,
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
      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
    />
  );
};
