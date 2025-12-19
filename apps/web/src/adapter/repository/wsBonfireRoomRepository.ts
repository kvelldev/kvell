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
  BonfireRoomCallbacks,
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

  connect(bonfireId: string, callbacks: BonfireRoomCallbacks): () => void {
    const wsUrl = `${this.baseWsUrl}/api/bonfires/${bonfireId}/ws`;
    const ws = new WebSocket(wsUrl);
    let isDisposed = false;

    ws.addEventListener("message", (event) => {
      if (isDisposed) return;
      try {
        const rawData = JSON.parse(event.data as string) as WebSocketMessage;

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
          callbacks.onSpark(spark);
        } else {
          // BonfireEvent: decayed or extended
          const bonfireEvent: BonfireEvent = {
            eventType: rawData.type,
            bonfireId: rawData.bonfire_id,
            message: rawData.message,
          };
          callbacks.onBonfireEvent(bonfireEvent);
        }
      } catch (error) {
        console.error("Failed to parse bonfire WebSocket message:", error);
      }
    });

    ws.addEventListener("error", (event) => {
      if (isDisposed) return;
      console.error("Bonfire WebSocket error:", event);
      callbacks.onError();
    });

    ws.addEventListener("close", (event) => {
      if (isDisposed) return;
      // Only trigger error callback on abnormal closures
      if (!event.wasClean) {
        console.error(
          "Bonfire WebSocket closed unexpectedly:",
          event.code,
          event.reason,
        );
        callbacks.onError();
      }
    });

    // Cleanup function to close WebSocket
    return () => {
      isDisposed = true;
      if (
        ws.readyState === WebSocket.OPEN ||
        ws.readyState === WebSocket.CONNECTING
      ) {
        ws.close();
      }
    };
  }
}

/**
 * Singleton instance of WebSocket BonfireRoom Repository
 */
export const wsBonfireRoomRepository: IBonfireRoomRepository =
  new WsBonfireRoomRepositoryImpl();
