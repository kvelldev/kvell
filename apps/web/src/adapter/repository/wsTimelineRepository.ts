/**
 * WebSocket Timeline Repository Implementation
 *
 * Adapter layer implementation of ITimelineRepository.
 * Handles WebSocket connection for real-time spark streaming.
 */

import type { Spark } from "@/domain/model/spark";
import type { ITimelineRepository } from "@/domain/repository/timelineRepository";
import type { TimelineEvent } from "@/domain/model/timelineEvent";

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

interface SparkPostedMessage {
  type: "spark_posted";
  data: SparkWebSocketMessage;
}

interface SparkUpdatedMessage {
  type: "spark_updated";
  spark_id: string;
  level: string;
  decay_at: string;
  bonfire_id?: string | null;
}

type WebSocketMessage =
  | SparkPostedMessage
  | SparkUpdatedMessage
  | SparkWebSocketMessage;

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

  connect(
    onMessage: (event: TimelineEvent) => void,
    onError: () => void,
  ): () => void {
    const ws = new WebSocket(this.wsUrl);
    let isDisposed = false;

    ws.addEventListener("message", (event) => {
      if (isDisposed) return;
      try {
        const data = JSON.parse(event.data as string) as WebSocketMessage;

        // Determine message type and map to domain models
        if ("type" in data && data.type === "spark_updated") {
          // Handle SparkUpdatedEvent
          onMessage({
            type: "spark_updated",
            spark_id: data.spark_id,
            level: data.level as any,
            decay_at: data.decay_at,
            bonfire_id: data.bonfire_id,
          });
        } else if (
          ("type" in data && data.type === "spark_posted") ||
          ("id" in data && "content" in data)
        ) {
          // Handle SparkPostedEvent (Explicit type OR Legacy flat object)
          const rawSpark =
            "type" in data && "data" in data
              ? data.data
              : (data as SparkWebSocketMessage);

          const spark: Spark = {
            id: rawSpark.id,
            content: rawSpark.content,
            userHash: rawSpark.user_hash,
            createdAt: rawSpark.created_at,
            decayAt: rawSpark.decay_at,
          };

          onMessage({
            type: "spark_posted",
            data: spark,
          });
        }
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
      if (!event.wasClean) {
        console.error(
          "WebSocket closed unexpectedly:",
          event.code,
          event.reason,
        );
        onError();
      }
    });

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
