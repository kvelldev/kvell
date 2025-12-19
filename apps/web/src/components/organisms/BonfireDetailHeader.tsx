/**
 * BonfireDetailHeader Organism (Dumb)
 *
 * Header section for bonfire detail view.
 * Displays the parent spark content, heat score, and action buttons.
 * Props-driven, no business logic.
 */

import { X, Flame, Share2 } from "lucide-react";
import clsx from "clsx";
import Linkify from "linkify-react";
import type { BonfireViewModel } from "@/domain/model/bonfire";
import { BonfireHeroImage } from "@/components/molecules/BonfireHeroImage";

/**
 * Props for BonfireDetailHeader
 */
export interface BonfireDetailHeaderProps {
  bonfire: BonfireViewModel;
  isDecayed: boolean;
  onClose: () => void;
  onAddFuel: () => void;
  onShare: () => void;
}

export const BonfireDetailHeader = ({
  bonfire,
  isDecayed,
  onClose,
  onAddFuel,
  onShare,
}: BonfireDetailHeaderProps) => {
  // Determine what to show: Custom Image or Default
  // const showCustomImage = !!currentSrc && !hasError; // Moved to BonfireHeroImage

  return (
    <div className="relative h-64 w-full shrink-0 md:h-80">
      {/* Background Image with layoutId for Hero Animation */}
      <BonfireHeroImage
        bonfireId={bonfire.id}
        image={bonfire.imageUrl ?? undefined}
        key={bonfire.imageUrl?.primaryUrl} // Reset state when URL changes
      />

      {/* Gradient Overlay - top 70% to bottom 95% transparency */}
      <div className="from-night-900 via-night-900/50 pointer-events-none absolute inset-0 bg-linear-to-t to-transparent" />

      {/* Close Button */}
      <button
        onClick={onClose}
        className={clsx(
          "absolute top-4 left-4 z-10",
          "flex size-10 items-center justify-center",
          "rounded-button bg-night-800/60 backdrop-blur-sm",
          "border border-white/10",
          "text-smoke-100 hover:bg-night-800/80 transition-colors",
        )}
        data-testid="close-button"
        aria-label="閉じる"
      >
        <X className="size-5" />
      </button>

      {/* Content Overlay */}
      <div className="absolute inset-x-0 bottom-0 z-10 p-4">
        {/* Parent Spark Content */}
        <p className="text-smoke-100 mb-3 text-base leading-relaxed md:text-lg">
          <Linkify
            options={{
              target: "_blank",
              rel: "noopener noreferrer",
              className:
                "text-ember-500/70 hover:underline text-ember-400 font-medium",
              nl2br: true,
              format: (value: string) =>
                value.length > 30 ? value.slice(0, 30) + "..." : value,
            }}
          >
            {bonfire.content}
          </Linkify>
        </p>
        {/* Actions Row */}
        <div className="flex items-center justify-between">
          {/* Heat Score (勢い) */}
          <div className={clsx("flex items-center gap-2", "text-ember-500")}>
            <Flame className="size-5" />
            <span className="text-sm font-medium">
              勢い: {bonfire.heatScore}
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Add Fuel Button */}
            <button
              onClick={onAddFuel}
              disabled={isDecayed}
              className={clsx(
                "rounded-button flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-all",
                "border-ember-500/30 bg-ember-500/10 text-ember-500 border",
                isDecayed
                  ? "cursor-not-allowed opacity-50"
                  : "hover:border-ember-500/50 hover:bg-ember-500/20",
              )}
              data-testid="header-add-fuel-button"
            >
              <Flame className="size-3.5" />
              <span>薪をくべる</span>
            </button>

            {/* Share Button */}
            <button
              onClick={onShare}
              disabled={isDecayed}
              className={clsx(
                "rounded-button flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-all",
                "text-smoke-100 border border-white/20 bg-white/5",
                isDecayed
                  ? "cursor-not-allowed opacity-50"
                  : "hover:border-white/30 hover:bg-white/10",
              )}
              data-testid="share-button"
            >
              <Share2 className="size-3.5" />
              <span>シェア</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
