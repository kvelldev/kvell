/**
 * TimelineStream Organism Component (Dumb)
 *
 * Virtual scrolling timeline with fade-out effect at the top boundary.
 * Pure presentational component - receives all data via props.
 */

import { Virtuoso } from "react-virtuoso";
import type { Spark } from "@/domain/model/spark";
import { SparkCard } from "@/components/atoms/SparkCard";

/**
 * Props for TimelineStream component
 */
interface TimelineStreamProps {
  /**
   * Array of sparks to display (ascending order - oldest first, newest last)
   */
  sparks: Spark[];
}

/**
 * TimelineStream Component
 *
 * Features:
 * - Virtual scrolling for performance (react-virtuoso)
 * - Auto-scroll to bottom when new sparks arrive
 * - Fade-out mask at top boundary (20% chimney effect)
 * - Color temperature based heat expression (handled by SparkCard)
 * @returns Rendered timeline stream element
 */
export const TimelineStream = ({ sparks }: TimelineStreamProps) => {
  return (
    <div
      className="relative size-full"
      style={{
        // Fade-out mask at top 20% (chimney effect - sparks vanish into the sky)
        maskImage:
          "linear-gradient(to bottom, transparent 0%, black 20%, black 100%)",
        WebkitMaskImage:
          "linear-gradient(to bottom, transparent 0%, black 20%, black 100%)",
      }}
      data-testid="timeline-stream"
    >
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
