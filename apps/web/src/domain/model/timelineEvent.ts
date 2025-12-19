/**
 * Timeline Event Types
 *
 * Defines the structure of events received via WebSocket.
 */

import type { Spark } from "@/domain/model/spark";
import type { SparkLevel } from "@/domain/model/spark";

/**
 * Event received when a new spark is posted.
 */
export interface SparkPostedEvent {
  type: "spark_posted";
  data: Spark;
}

/**
 * Event received when a spark's state is updated (promotion, decay extension).
 */
export interface SparkUpdatedEvent {
  type: "spark_updated";
  spark_id: string;
  level: SparkLevel; // Enum value (string)
  decay_at: string;
  bonfire_id?: string | null;
}

/**
 * Union type for all timeline events.
 */
export type TimelineEvent = SparkPostedEvent | SparkUpdatedEvent;
