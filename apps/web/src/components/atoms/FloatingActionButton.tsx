/**
 * FloatingActionButton Atom
 *
 * A floating action button that appears in the bottom-right corner.
 * Generic component without domain-specific styling.
 */

import { Button } from "@/components/ui/button";
import type { ReactNode } from "react";

interface FloatingActionButtonProps {
  onClick: () => void;
  icon: ReactNode;
  label?: string;
  testId?: string;
}

export const FloatingActionButton = ({
  onClick,
  icon,
  label,
  testId,
}: FloatingActionButtonProps) => {
  return (
    <Button
      onClick={onClick}
      size="icon"
      className="shadow-glow-md hover:shadow-glow-md fixed right-4 bottom-4 h-12 w-12 rounded-full opacity-40 transition-all hover:scale-110 hover:opacity-100 sm:right-6 sm:bottom-6 sm:h-14 sm:w-14"
      data-testid={testId}
      aria-label={label}
    >
      {icon}
    </Button>
  );
};
