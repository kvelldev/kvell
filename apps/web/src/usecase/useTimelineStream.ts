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
import {
  useResilientConnection,
  type ConnectionStatus,
} from "./useResilientConnection";
import { useSparkBatcher } from "./useSparkBatcher";
import { useSparkTransformer } from "./useSparkTransformer";

export type { ConnectionStatus };

interface UseTimelineStreamProps {
  repository: ITimelineRepository;
  onBonfirePromoted?: () => void;
}

/**
 * Timeline Stream Custom Hook
 * @param repository - Timeline repository implementation (DIP)
 * @param onBonfirePromoted - Callback triggers when a spark is promoted to Bonfire
 * @returns Object containing current spark ViewModels and connection error state
 */
export const useTimelineStream = ({
  repository,
  onBonfirePromoted,
}: UseTimelineStreamProps) => {
  // 1. Data Management (Buffering & State Updates)
  const { sparks, pushEvent } = useSparkBatcher(onBonfirePromoted);

  // 2. Connection Management (Connection & Reconnection)
  const status = useResilientConnection(repository, pushEvent);

  // 3. View Transformation (TTL & Temperature)
  const viewModels = useSparkTransformer(sparks);

  return { sparks: viewModels, status };
};
