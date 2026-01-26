/**
 * Timeline Stream UseCase
 *
 * Business logic for real-time timeline spark streaming.
 * Manages WebSocket connection, spark accumulation, deduplication, TTL cleanup,
 * and temperature calculation for UI rendering.
 *
 * Implements batching for incoming events to reduce render frequency.
 */

import type { ITimelineRepository } from "@/domain/repository/timelineRepository";
import { useResilientWebSocket } from "./useResilientConnection";
import { useSparkBatcher } from "./useSparkBatcher";
import { useSparkTransformer } from "./useSparkTransformer";

interface UseTimelineStreamProps {
  repository: ITimelineRepository;
  fieldId: string;
  onBonfirePromoted?: () => void;
}

/**
 * Timeline Stream Custom Hook
 * @param props - Hook properties
 * @param props.repository - Timeline repository implementation (DIP)
 * @param props.fieldId - The field (community) ID to stream from
 * @param props.onBonfirePromoted - Callback triggers when a spark is promoted to Bonfire
 * @returns Object containing current spark ViewModels and connection error state
 */
export const useTimelineStream = ({
  repository,
  fieldId,
  onBonfirePromoted,
}: UseTimelineStreamProps) => {
  // 1. Data Management (Buffering & State Updates)
  const { sparks, pushEvent } = useSparkBatcher(onBonfirePromoted);

  // 2. Connection Management (Connection & Reconnection)
  const status = useResilientWebSocket(
    repository.getConnectionUrl(fieldId),
    (message) => repository.parseMessage(message),
    pushEvent,
  );

  // 3. View Transformation (TTL & Temperature)
  const viewModels = useSparkTransformer(sparks);

  return { sparks: viewModels, status };
};

export { type ConnectionStatus } from "./useResilientConnection";
