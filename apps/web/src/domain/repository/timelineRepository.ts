/**
 * Timeline Repository Interface (DIP)
 *
 * Abstract definition of real-time timeline data streaming operations.
 * Manages WebSocket connection lifecycle and spark streaming.
 */

import type { TimelineEvent } from "@/domain/model/timelineEvent";

/**
 * Timeline Repository Interface
 *
 * Provides real-time streaming of timeline events via WebSocket connection.
 */
export interface ITimelineRepository {
  /**
   * Establish WebSocket connection and start receiving timeline events.
   * @param onMessage - Callback invoked when a new event is received
   * @param onError - Callback invoked when connection fails or closes unexpectedly
   * @returns Cleanup function to disconnect and close the WebSocket
   */
  connect(
    onMessage: (event: TimelineEvent) => void,
    onError: () => void,
  ): () => void;
}
