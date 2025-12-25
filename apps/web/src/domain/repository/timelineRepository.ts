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
  /**
   * The WebSocket URL to connect to.
   */
  readonly connectionUrl: string;

  /**
   * Parse a raw WebSocket message into a domain event.
   * @param message - The raw message received from the WebSocket
   * @returns The parsed TimelineEvent, or null if the message is invalid or irrelevant
   */
  parseMessage(message: unknown): TimelineEvent | null;
}
