/**
 * WebSocket Timeline Repository Implementation
 *
 * Adapter layer implementation of ITimelineRepository.
 * Handles WebSocket connection for real-time spark streaming.
 */

import type { Spark } from "@/domain/model/spark";
import type { ITimelineRepository } from "@/domain/repository/timelineRepository";

/**
 * WebSocket message response type (snake_case from backend)
 */
interface SparkWebSocketMessage {
  id: string;
  content: string;
  user_hash: string;
  created_at: string;
  decay_at: string;
}

/**
 * WebSocket Timeline Repository Implementation
 */
class WsTimelineRepositoryImpl implements ITimelineRepository {
  private readonly wsUrl: string;

  constructor() {
    const baseUrl: string =
      (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
      "http://localhost:8000";
    // Convert http(s):// to ws(s)://
    this.wsUrl = baseUrl.replace(/^http/, "ws") + "/api/sparks/ws";
  }

  connect(onMessage: (spark: Spark) => void, onError: () => void): () => void {
    const ws = new WebSocket(this.wsUrl);
    let isDisposed = false;

    ws.addEventListener("message", (event) => {
      if (isDisposed) return;
      try {
        const rawData = JSON.parse(
          event.data as string,
        ) as SparkWebSocketMessage;

        // Transform snake_case to camelCase domain model
        const spark: Spark = {
          id: rawData.id,
          content: rawData.content,
          userHash: rawData.user_hash,
          createdAt: rawData.created_at,
          decayAt: rawData.decay_at,
        };

        onMessage(spark);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    });

    ws.addEventListener("error", (event) => {
      if (isDisposed) return;
      console.error("WebSocket error:", event);
      onError();
    });

    ws.addEventListener("close", (event) => {
      if (isDisposed) return;
      // Only trigger error callback on abnormal closures
      if (!event.wasClean) {
        console.error(
          "WebSocket closed unexpectedly:",
          event.code,
          event.reason,
        );
        onError();
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
 * Singleton instance of WebSocket Timeline Repository
 */
export const wsTimelineRepository: ITimelineRepository =
  new WsTimelineRepositoryImpl();
