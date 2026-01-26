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
  private readonly _baseUrl: string;

  constructor() {
    const baseUrl: string =
      (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
      "http://localhost:8000";
    // Convert http(s):// to ws(s)://
    this._baseUrl = baseUrl.replace(/^http/, "ws");
  }

  getConnectionUrl(fieldId: string): string {
    return `${this._baseUrl}/api/sparks/${fieldId}/ws`;
  }

  parseMessage(message: unknown): TimelineEvent | null {
    try {
      // In react-use-websocket, message.data is the string content if configured,
      // but let's assume raw message event or already parsed data depending on usage.
      // Actually, useWebSocket's lastJsonMessage or manually parsing 'message' usually needed.
      // If 'message' passed here is the raw MessageEvent.data string:

      // However, let's look at how we'll call it.
      // If we pass the parsed JSON object directly (from lastJsonMessage), 'message' is an object.
      // If we pass the raw event data, it's a string.
      // Let's handle both for robustness, or assume object if we use lastJsonMessage.

      // WsTimelineRepositoryImpl previously parsed JSON.
      // Let's assume input is the raw string or parsed object.
      // Safe implementation:

      let data: WebSocketMessage;

      if (typeof message === "string") {
        data = JSON.parse(message) as WebSocketMessage;
      } else {
        data = message as WebSocketMessage;
      }

      // Determine message type and map to domain models
      if ("type" in data && data.type === "spark_updated") {
        // Handle SparkUpdatedEvent
        return {
          type: "spark_updated",
          spark_id: data.spark_id,
          level: data.level as any,
          decay_at: data.decay_at,
          bonfire_id: data.bonfire_id,
        };
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

        return {
          type: "spark_posted",
          data: spark,
        };
      }
    } catch (error) {
      console.error("Failed to parse WebSocket message:", error);
    }
    return null;
  }
}

/**
 * Singleton instance of WebSocket Timeline Repository
 */
export const wsTimelineRepository: ITimelineRepository =
  new WsTimelineRepositoryImpl();
