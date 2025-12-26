/**
 * BonfireCard Component (Molecule)
 *
 * Displays a single bonfire (promoted spark) with:
 * - Glassmorphism design (translucent background + blur)
 * - Glow effect (shadow-glow)
 * - Default bonfire image
 * - Content with heat score indicator
 * - Shared Element Transition support via Framer Motion layoutId
 *
 * Visual style follows SparkCard patterns and Design Token guidelines.
 * Uses shadcn/ui Card as base component.
 */

import { memo, useState } from "react";
import clsx from "clsx";
import { Flame } from "lucide-react";
import { motion } from "framer-motion";
import type { BonfireViewModel } from "@/domain/model/bonfire";
import { Card, CardContent } from "@/components/ui/card";
import defaultImage from "@/assets/bonfire_default.png";

interface BonfireCardProps {
  bonfire: BonfireViewModel;
  onClick?: (bonfire: BonfireViewModel) => void;
}

/**
 * BonfireCard Component (Memoized)
 *
 * Performance:
 * - Memoized to prevent unnecessary re-renders
 * @returns Rendered bonfire card element
 */
const BonfireCardComponent = ({ bonfire, onClick }: BonfireCardProps) => {
  const handleClick = () => {
    onClick?.(bonfire);
  };

  const hasCustomImage = !!bonfire.imageUrl?.primaryUrl;
  const imageUrl = bonfire.imageUrl?.primaryUrl;
  const [imgError, setImgError] = useState(false);

  return (
    <Card
      className={clsx(
        // Layout & Responsive dimensions (mobile: smaller, md: larger)
        "h-52 w-52 md:h-72 md:w-72",
        "flex-none snap-center overflow-hidden transition-all duration-300",
        "hover:scale-[1.02]",

        // Base Style
        "text-smoke-100",
        "bg-night-900/40 backdrop-blur-md",
        "border border-white/10", // 「ガラスのエッジ」を表現
        "shadow-lg", // 通常時は黒い影で浮き上がらせる

        // Hover Interaction (点火: 熱量と光)
        "hover:border-ember-500/30", // 触ると枠が熱くなる
        "hover:shadow-glow-sm", // 触ると光が漏れる (Design Tokenの影)

        // Clickable
        onClick && "cursor-pointer",
      )}
      data-testid="bonfire-item"
      onClick={handleClick}
    >
      {/* Image Section with layoutId for Shared Element Transition */}
      <motion.div
        className="relative h-28 w-full overflow-hidden bg-black/40 md:h-40"
        layoutId={`bonfire-image-${bonfire.id}`}
      >
        {hasCustomImage && !imgError ? (
          <>
            {/* Background: Blur & Cover */}
            <img
              src={imageUrl}
              alt=""
              className="absolute inset-0 h-full w-full object-cover opacity-50 blur-xl"
            />
            {/* Foreground: Contain & Clear */}
            <img
              src={imageUrl}
              alt="Bonfire"
              className="relative h-full w-full object-contain transition-transform duration-500 hover:scale-105"
              onError={() => setImgError(true)}
            />
          </>
        ) : (
          /* Default Image */
          <img
            src={defaultImage}
            alt="Bonfire"
            className="h-full w-full object-cover transition-transform duration-500 hover:scale-110"
          />
        )}
        {/* Gradient overlay for text readability */}
        <div className="from-night-900/80 absolute inset-0 bg-linear-to-t to-transparent" />

        {/* Heat Score Badge */}
        <div
          className={clsx(
            "absolute right-2 bottom-2",
            "flex items-center gap-1",
            "rounded-button px-2 py-0.5",
            "border-ember-500/30 bg-ember-500/10 border backdrop-blur-sm",
            "text-ember-500 text-xs",
          )}
        >
          <Flame className="size-3" />
          <span>{bonfire.heatScore}</span>
        </div>
      </motion.div>

      {/* Content Section - Responsive height with text truncation */}
      <CardContent className="h-16 p-3 md:h-20 md:p-4">
        <p className="font-base text-smoke-100 line-clamp-2 text-sm leading-relaxed">
          {bonfire.content}
        </p>
      </CardContent>
    </Card>
  );
};

export const BonfireCard = memo(BonfireCardComponent);
