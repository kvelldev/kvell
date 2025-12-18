/**
 * BonfireRoom Repository Interface (DIP)
 *
 * Abstract definition of WebSocket connection operations for
 * real-time bonfire room communication.
 */

import type { Spark } from "@/domain/model/spark";
import type { BonfireEvent } from "@/domain/model/bonfireEvent";

/**
 * Callbacks for bonfire room events
 */
export interface BonfireRoomCallbacks {
  /**
   * Called when a new spark (reply) is received
   */
  onSpark: (spark: Spark) => void;

  /**
   * Called when a bonfire lifecycle event occurs (decayed/extended)
   */
  onBonfireEvent: (event: BonfireEvent) => void;

  /**
   * Called when a WebSocket error occurs
   */
  onError: () => void;
}

/**
 * BonfireRoom Repository Interface
 */
export interface IBonfireRoomRepository {
  /**
   * Connect to a bonfire room via WebSocket.
   * @param bonfireId - The bonfire ID to connect to
   * @param callbacks - Event callbacks
   * @returns Cleanup function to disconnect
   */
  connect(bonfireId: string, callbacks: BonfireRoomCallbacks): () => void;
}
