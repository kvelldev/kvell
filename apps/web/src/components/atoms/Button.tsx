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
    "px-4 py-2 rounded-button font-light transition-all disabled:opacity-ash disabled:cursor-not-allowed";
  const variantClasses =
    variant === "primary"
      ? "bg-ember-500 hover:shadow-glow-md text-night-900"
      : "bg-night-800 hover:shadow-glow-sm text-smoke-100";

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
