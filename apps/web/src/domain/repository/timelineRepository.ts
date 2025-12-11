/**
 * Timeline Repository Interface (DIP)
 *
 * Abstract definition of real-time timeline data streaming operations.
 * Manages WebSocket connection lifecycle and spark streaming.
 */

import type { Spark } from "@/domain/model/spark";

/**
 * Timeline Repository Interface
 *
 * Provides real-time streaming of sparks via WebSocket connection.
 */
export interface ITimelineRepository {
  /**
   * Establish WebSocket connection and start receiving spark messages.
   * @param onMessage - Callback invoked when a new spark is received
   * @param onError - Callback invoked when connection fails or closes unexpectedly
   * @returns Cleanup function to disconnect and close the WebSocket
   */
  connect(onMessage: (spark: Spark) => void, onError: () => void): () => void;
}
