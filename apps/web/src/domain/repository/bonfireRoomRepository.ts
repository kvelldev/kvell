/**
 * BonfireRoom Repository Interface (DIP)
 *
 * Abstract definition of WebSocket connection operations for
 * real-time bonfire room communication.
 */

import type { Spark } from "@/domain/model/spark";
import type { BonfireEvent } from "@/domain/model/bonfireEvent";

/**
 *
 */
export type ParsedBonfireMessage =
  | { type: "spark"; data: Spark }
  | { type: "bonfire_event"; data: BonfireEvent };

/**
 * BonfireRoom Repository Interface
 *
 * Provides connection information and message parsing for Bonfire Rooms.
 * Connection management is delegated to the UseCase layer.
 */
export interface IBonfireRoomRepository {
  /**
   * Get the WebSocket URL for a specific bonfire room.
   * @param bonfireId - The bonfire ID
   */
  getConnectionUrl(bonfireId: string): string;

  /**
   * Parse a raw WebSocket message into a domain entity.
   * @param message - Raw message data
   */
  parseMessage(message: unknown): ParsedBonfireMessage | null;
}
