/**
 * ErrorStateMessage Molecule Component (Dumb)
 *
 * Generic error state message display.
 * Used for showing error conditions with title and description.
 */

/**
 * Props for ErrorStateMessage component
 */
interface ErrorStateMessageProps {
  /**
   * Error title (main message)
   */
  title: string;

  /**
   * Error description (supporting text)
   */
  description: string;

  /**
   * Optional test ID
   */
  testId?: string;
}

/**
 * ErrorStateMessage Component
 *
 * Features:
 * - Centered layout
 * - Two-level text hierarchy (title + description)
 * - Smoke color for title, ash color for description
 * @returns Rendered error state message
 */
export const ErrorStateMessage = ({
  title,
  description,
  testId,
}: ErrorStateMessageProps) => {
  return (
    <div
      className="flex size-full items-center justify-center"
      data-testid={testId}
    >
      <div className="text-center">
        <p className="mb-4 font-base text-xl text-smoke-100">{title}</p>
        <p className="font-base text-sm text-ash-500">{description}</p>
      </div>
    </div>
  );
};
