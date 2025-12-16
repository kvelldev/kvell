/**
 * BonfireDetailOverlay Component
 *
 * Full-screen overlay for viewing bonfire details and responses.
 * Features:
 * - Shared Element Transition (Hero Animation) with BonfireCard
 * - Header with background image, gradient overlay, and bonfire info
 * - Response timeline with react-virtuoso
 * - "Read up to here" marker
 * - FAB for posting responses
 *
 * This is a mock implementation without data fetching.
 */

import clsx from "clsx";
import { motion, AnimatePresence } from "framer-motion";
import { Virtuoso } from "react-virtuoso";
import { X, Flame, Share2 } from "lucide-react";
import type { Bonfire } from "@/domain/model/bonfire";
import type { SparkViewModel } from "@/domain/model/spark";
import defaultImage from "@/assets/bonfire_default.png";

interface BonfireDetailOverlayProps {
  bonfire: Bonfire | null;
  isOpen: boolean;
  onClose: () => void;
}

// Mock response data for the timeline
const generateMockResponses = (bonfireId: string): SparkViewModel[] => {
  const mockContents = [
    "これめっちゃわかる！自分も同じこと思ってた",
    "いやほんとそれな。今日の試合熱かったよね",
    "推しが輝いてる瞬間を共有できるの最高すぎる",
    "この話題で盛り上がれるの嬉しい！",
    "さっきのプレー見た？神がかってたわ",
    "みんなで応援してる感じがたまらん",
    "今日イチの名場面だと思う",
    "同じ気持ちの人がいて安心した笑",
  ];

  return mockContents.map((content, index) => ({
    id: `${bonfireId}-response-${String(index)}`,
    content,
    createdAt: new Date(
      Date.now() - (mockContents.length - index) * 60_000,
    ).toISOString(),
    decayAt: new Date(Date.now() + 300_000).toISOString(),
    temperature: "hot" as const,
    remainingTimeInSeconds: 300 - index * 30,
  }));
};

// Handlers defined outside component (no dependency on props/state)
const handleShare = () => {
  console.info("Share dialog would open here");
};

const handlePostClick = () => {
  console.info("Post modal would open here");
};

// Index of the "read up to here" marker (mock: show after 3rd item)
const READ_MARKER_INDEX = 3;

/**
 * Response card without fuel button (for bonfire responses)
 * @returns Rendered response card element
 */
const ResponseCard = ({ spark }: { spark: SparkViewModel }) => {
  return (
    <div
      className={clsx(
        "rounded-card bg-night-800/40 p-4 backdrop-blur-md",
        "border border-white/10",
        "text-ash-500",
      )}
      data-testid="response-item"
    >
      <p className="font-base line-clamp-3 text-sm leading-relaxed">
        {spark.content}
      </p>
    </div>
  );
};

/**
 * "Read up to here" marker component
 * @returns Rendered read marker element
 */
const ReadMarker = () => {
  return (
    <div className="flex items-center gap-3 py-4" data-testid="read-marker">
      <div className="bg-ash-500/30 h-px flex-1" />
      <span className="text-ash-500 text-xs">ここまで読んだ</span>
      <div className="bg-ash-500/30 h-px flex-1" />
    </div>
  );
};

export const BonfireDetailOverlay = ({
  bonfire,
  isOpen,
  onClose,
}: BonfireDetailOverlayProps) => {
  // Generate mock responses when bonfire is available
  const responses = bonfire ? generateMockResponses(bonfire.id) : [];

  const handleAddFuel = () => {
    console.info("Adding fuel to bonfire:", bonfire?.id);
  };

  return (
    <AnimatePresence>
      {isOpen && bonfire && (
        <motion.div
          className="bg-night-900 fixed inset-0 z-50 flex flex-col"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          data-testid="bonfire-detail-overlay"
        >
          {/* Header Area */}
          <div className="relative h-64 w-full flex-shrink-0 md:h-80">
            {/* Background Image with layoutId for Hero Animation */}
            <motion.div
              className="absolute inset-0"
              layoutId={`bonfire-image-${bonfire.id}`}
            >
              <img
                src={defaultImage}
                alt="Bonfire"
                className="h-full w-full object-cover"
              />
            </motion.div>

            {/* Gradient Overlay */}
            <div
              className={clsx(
                "absolute inset-0",
                "from-night-900 bg-linear-to-t to-transparent",
              )}
            />

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
                {bonfire.content}
              </p>

              {/* Actions Row */}
              <div className="flex items-center justify-between">
                {/* Heat Score (勢い) */}
                <div
                  className={clsx("flex items-center gap-2", "text-ember-500")}
                >
                  <Flame className="size-5" />
                  <span className="text-sm font-medium">
                    勢い: {bonfire.heatScore}
                  </span>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2">
                  {/* Add Fuel Button */}
                  <button
                    onClick={handleAddFuel}
                    className={clsx(
                      "rounded-button flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-all",
                      "border-ember-500/30 bg-ember-500/10 text-ember-500 border",
                      "hover:border-ember-500/50 hover:bg-ember-500/20",
                    )}
                    data-testid="header-add-fuel-button"
                  >
                    <Flame className="size-3.5" />
                    <span>薪をくべる</span>
                  </button>

                  {/* Share Button */}
                  <button
                    onClick={handleShare}
                    className={clsx(
                      "rounded-button flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-all",
                      "text-smoke-100 border border-white/20 bg-white/5",
                      "hover:border-white/30 hover:bg-white/10",
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

          {/* Response Timeline */}
          <div className="flex-1 overflow-hidden">
            <Virtuoso
              data={responses}
              initialTopMostItemIndex={0}
              computeItemKey={(_, spark) => spark.id}
              itemContent={(index, spark) => (
                <>
                  {/* Show "Read up to here" marker after specific index */}
                  {index === READ_MARKER_INDEX && <ReadMarker />}
                  <div className="px-4 pb-4">
                    <ResponseCard spark={spark} />
                  </div>
                </>
              )}
              style={{ height: "100%" }}
            />
          </div>

          {/* Floating Action Button */}
          <button
            onClick={handlePostClick}
            className={clsx(
              "fixed right-4 bottom-6 z-50",
              "flex size-14 items-center justify-center",
              "rounded-button",
              "bg-ember-500 text-white",
              "shadow-glow-sm",
              "transition-transform hover:scale-105 active:scale-95",
            )}
            data-testid="response-post-fab"
            aria-label="レスを投稿"
          >
            <Flame className="size-6" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
