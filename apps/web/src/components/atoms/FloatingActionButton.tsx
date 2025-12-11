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
      size="lg"
      className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-glow-md transition-all hover:scale-110 hover:shadow-glow-md"
      data-testid={testId}
      aria-label={label}
    >
      {icon}
    </Button>
  );
};
