/**
 * TimelineStream Organism Component (Dumb)
 *
 * YouTube Live-style scrolling timeline for real-time spark display.
 * Pure presentational component - receives all data via props.
 */

import { Virtuoso } from "react-virtuoso";
import type { SparkViewModel } from "@/domain/model/spark";
import { SparkCard } from "@/components/atoms/SparkCard";

/**
 * Props for TimelineStream component
 */
interface TimelineStreamProps {
  /**
   * Array of spark ViewModels to display (ascending order - oldest first, newest last)
   */
  sparks: SparkViewModel[];
}

/**
 * TimelineStream Component
 *
 * Features:
 * - Virtual scrolling for performance (react-virtuoso)
 * - Auto-scroll to bottom when new sparks arrive (followOutput="auto")
 * - Initial display at bottom (YouTube Live-style)
 * - Color temperature based heat expression (handled by SparkCard)
 * - Empty state display when no sparks are available
 * @returns Rendered timeline stream element
 */
export const TimelineStream = ({ sparks }: TimelineStreamProps) => {
  // Empty State: Display "The Silent Sky" when no sparks are available
  if (sparks.length === 0) {
    return (
      <div
        className="flex size-full items-center justify-center"
        data-testid="timeline-stream"
      >
        <p
          className="font-base text-sm text-ash-500"
          data-testid="timeline-empty-state"
        >
          静かな夜空です。
        </p>
      </div>
    );
  }

  return (
    <div className="relative size-full" data-testid="timeline-container">
      <Virtuoso
        data={sparks}
        followOutput="auto"
        initialTopMostItemIndex={sparks.length > 0 ? sparks.length - 1 : 0}
        itemContent={(_index, spark) => (
          <div className="mb-4">
            <SparkCard spark={spark} />
          </div>
        )}
        style={{ height: "100%" }}
      />
    </div>
  );
};
