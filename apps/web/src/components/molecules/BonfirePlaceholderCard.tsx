/**
 * BonfirePlaceholderCard Component (Molecule)
 *
 * Displays a placeholder card when no bonfires exist.
 * Shares visual style with BonfireCard (Glassmorphism, same dimensions).
 *
 * Uses subtle Info icon instead of bonfire image to indicate empty state.
 */

import clsx from "clsx";
import { Info } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface BonfirePlaceholderCardProps {
  message: string;
}

export const BonfirePlaceholderCard = ({
  message,
}: BonfirePlaceholderCardProps) => {
  return (
    <Card
      className={clsx(
        // Layout & Responsive dimensions (same as BonfireCard)
        "h-52 w-52 md:h-72 md:w-72",
        "flex-none overflow-hidden",

        // Base Style (Glassmorphism)
        "bg-night-900/40 backdrop-blur-md",
        "border border-white/10",
      )}
      data-testid="bonfire-placeholder"
    >
      {/* Icon Section (replaces image) */}
      <div
        className={clsx(
          "relative h-28 w-full md:h-40",
          "flex items-center justify-center",
          "bg-earthshadow-base/20",
        )}
      >
        <Info className="text-ash-500 size-8 md:size-10" strokeWidth={1} />
      </div>

      {/* Content Section */}
      <CardContent className="h-16 p-3 md:h-20 md:p-4">
        <p className="font-base text-ash-500 text-center text-sm leading-relaxed">
          {message}
        </p>
      </CardContent>
    </Card>
  );
};
