/**
 * Button Atom
 *
 * Basic button component (Stateless).
 */

interface ButtonProps {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  variant?: "primary" | "secondary";
  testId?: string;
}

export const Button = ({
  children,
  onClick,
  disabled = false,
  variant = "primary",
  testId,
}: ButtonProps) => {
  const baseClasses =
    "px-4 py-2 rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed";
  const variantClasses =
    variant === "primary"
      ? "bg-blue-600 hover:bg-blue-700 text-white"
      : "bg-gray-200 hover:bg-gray-300 text-gray-800";

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variantClasses}`}
      data-testid={testId}
    >
      {children}
    </button>
  );
};
