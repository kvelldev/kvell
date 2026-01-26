/**
 * WebSocket BonfireRoom Repository Implementation
 *
 * Adapter layer implementation of IBonfireRoomRepository.
 * Handles WebSocket connection for real-time bonfire room communication.
 * Receives both Spark (reply) messages and BonfireEvent (decayed/extended) messages.
 */

import type { Spark } from "@/domain/model/spark";
import type { BonfireEvent } from "@/domain/model/bonfireEvent";
import type {
  IBonfireRoomRepository,
  ParsedBonfireMessage,
} from "@/domain/repository/bonfireRoomRepository";

/**
 * WebSocket message response type for sparks (snake_case from backend)
 */
interface SparkWebSocketMessage {
  type: "spark";
  id: string;
  content: string;
  user_hash: string;
  created_at: string;
  decay_at: string;
  parent_bonfire_id?: string;
}

/**
 * WebSocket message response type for bonfire events (snake_case from backend)
 */
interface BonfireEventWebSocketMessage {
  type: "decayed" | "extended";
  bonfire_id: string;
  message?: string;
}

/**
 * Union type for all possible WebSocket messages
 */
type WebSocketMessage = SparkWebSocketMessage | BonfireEventWebSocketMessage;

/**
 * WebSocket BonfireRoom Repository Implementation
 */
class WsBonfireRoomRepositoryImpl implements IBonfireRoomRepository {
  private readonly baseWsUrl: string;

  constructor() {
    const baseUrl: string =
      (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
      "http://localhost:8000";
    // Convert http(s):// to ws(s)://
    this.baseWsUrl = baseUrl.replace(/^http/, "ws");
  }

  getConnectionUrl(bonfireId: string): string {
    return `${this.baseWsUrl}/api/bonfires/${bonfireId}/ws`;
  }

  parseMessage(message: unknown): ParsedBonfireMessage | null {
    try {
      const rawData = JSON.parse(message as string) as WebSocketMessage;

      if (rawData.type === "spark") {
        // Transform snake_case to camelCase domain model
        const spark: Spark = {
          id: rawData.id,
          content: rawData.content,
          userHash: rawData.user_hash,
          createdAt: rawData.created_at,
          decayAt: rawData.decay_at,
          parentBonfireId: rawData.parent_bonfire_id,
        };
        // Return wrapped message
        return { type: "spark", data: spark };
      } else {
        // BonfireEvent: decayed or extended
        const bonfireEvent: BonfireEvent = {
          eventType: rawData.type,
          bonfireId: rawData.bonfire_id,
          message: rawData.message,
        };
        return { type: "bonfire_event", data: bonfireEvent };
      }
    } catch (error) {
      console.error("Failed to parse bonfire WebSocket message:", error);
      return null;
    }
  }
}

/**
 * Singleton instance of WebSocket BonfireRoom Repository
 */
export const wsBonfireRoomRepository: IBonfireRoomRepository =
  new WsBonfireRoomRepositoryImpl();
