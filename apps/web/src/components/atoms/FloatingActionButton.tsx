/**
 * FloatingActionButton Atom Component (Dumb)
 *
 * A fixed-position floating action button (FAB) with icon and label.
 * Typically used for primary actions like "See More", "Add", etc.
 */

import type { ReactNode } from "react";

/**
 * Props for FloatingActionButton component
 */
interface FloatingActionButtonProps {
  /**
   * Button label text
   */
  label: string;

  /**
   * Icon element (e.g., from lucide-react)
   */
  icon: ReactNode;

  /**
   * Click handler
   */
  onClick: () => void;

  /**
   * Test ID for testing
   */
  testId?: string;
}

/**
 * FloatingActionButton Component
 *
 * Features:
 * - Fixed position at bottom-right
 * - Ember color with glow hover effect
 * - Icon + label layout
 * - Smooth transitions
 * @returns Rendered floating action button
 */
export const FloatingActionButton = ({
  label,
  icon,
  onClick,
  testId,
}: FloatingActionButtonProps) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 z-30 flex items-center gap-2 rounded-button bg-ember-500 px-6 py-3 text-smoke-100 transition-all duration-200 hover:bg-ember-500 hover:shadow-glow-md"
      data-testid={testId}
    >
      {icon}
      <span className="font-base text-sm">{label}</span>
    </button>
  );
};
