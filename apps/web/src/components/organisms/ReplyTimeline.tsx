/**
 * ReplyTimeline Organism Component (Dumb)
 *
 * Virtualized timeline for bonfire replies display.
 * Pure presentational component - receives all data via props.
 *
 * Features:
 * - Virtual scrolling for performance (react-virtuoso)
 * - Initial display at top (oldest first as per spec)
 * - ReadMarker at fixed position (LINE/Discord style - does not move during scroll)
 * - SparkCard without fuel button for each reply
 */

import { Virtuoso } from "react-virtuoso";
import type { SparkViewModel } from "@/domain/model/spark";
import { SparkCard } from "@/components/molecules/SparkCard";
import { ReadMarker } from "@/components/atoms/ReadMarker";

/**
 * Props for ReplyTimeline component
 */
interface ReplyTimelineProps {
  /**
   * Array of spark ViewModels to display (ascending order - oldest first)
   */
  sparks: SparkViewModel[];

  /**
   * Marker display position SparkID (fixed during session, does not move)
   * Shows "read up to here" marker after this spark
   */
  displayMarkerSparkId: string | null;

  /**
   * Callback when visible range changes (for tracking scroll position)
   * Reports sparkId and index for high water mark tracking
   */
  onVisiblePositionChange?: (sparkId: string, index: number) => void;
}

/**
 * ReplyTimeline Component
 *
 * Features:
 * - Virtual scrolling for performance (react-virtuoso)
 * - Initial display at top (oldest first, as per Gherkin spec)
 * - ReadMarker displayed after the display marker spark (fixed, LINE/Discord style)
 * - SparkCard with hideFuelButton (replies cannot be promoted)
 * @returns Rendered reply timeline element
 */
export const ReplyTimeline = ({
  sparks,
  displayMarkerSparkId,
  onVisiblePositionChange,
}: ReplyTimelineProps) => {
  // Find the index of the display marker spark (fixed position)
  const markerIndex = displayMarkerSparkId
    ? sparks.findIndex((s) => s.id === displayMarkerSparkId)
    : -1;

  // Only show marker if there are unread sparks after the marker position
  const shouldShowMarker = markerIndex >= 0 && markerIndex < sparks.length - 1;

  // Handle visible range change to track scroll position
  const handleRangeChange = (range: { startIndex: number; endIndex: number }) => {
    if (onVisiblePositionChange && sparks.length > 0) {
      const lastVisibleSpark = sparks.at(range.endIndex);
      if (lastVisibleSpark) {
        // Pass both sparkId and index for O(1) comparison in useReadMarker
        onVisiblePositionChange(lastVisibleSpark.id, range.endIndex);
      }
    }
  };

  // Empty State
  if (sparks.length === 0) {
    return (
      <div
        className="flex size-full items-center justify-center"
        data-testid="reply-timeline"
      >
        <p
          className="text-ash-500 font-base text-sm"
          data-testid="reply-timeline-empty-state"
        >
          まだレスがありません
        </p>
      </div>
    );
  }

  return (
    <div className="relative size-full" data-testid="reply-timeline-container">
      <Virtuoso
        data={sparks}
        initialTopMostItemIndex={Math.max(0, markerIndex)}
        followOutput="smooth"
        computeItemKey={(_, spark) => spark.id}
        rangeChanged={handleRangeChange}
        itemContent={(index, spark) => (
          <>
            {/* Show "Read up to here" marker after display marker spark (fixed position) */}
            {shouldShowMarker && index === markerIndex + 1 && <ReadMarker />}
            <div className="pr-2 pb-4">
              <SparkCard spark={spark} hideFuelButton />
            </div>
          </>
        )}
        style={{ height: "100%" }}
      />
    </div>
  );
};
