/**
 * Spark Domain Model
 *
 * Represents a single spark (種火) - the core unit of all topics in Kvell.
 */

import type { SparkTemperature } from "@/domain/service/sparkService";

/**
 * Spark interface
 */
export interface Spark {
  /**
   * Unique identifier for the spark
   */
  id: string;

  /**
   * Spark content text
   */
  content: string;

  /**
   * ISO timestamp when the spark was created
   */
  createdAt: string;

  /**
   * ISO timestamp when the spark decays (becomes invisible)
   */
  decayAt: string;

  /**
   * Parent bonfire ID if this spark is a reply to a bonfire
   * Undefined for standalone sparks
   */
  parentBonfireId?: string;
}

/**
 * Spark ViewModel with computed temperature state and remaining time
 * Used for UI rendering to avoid recalculation on every render
 */
export interface SparkViewModel extends Spark {
  /**
   * Computed temperature state ('hot' or 'ash')
   * Determines visual representation (color, border glow)
   */
  temperature: SparkTemperature;

  /**
   * Remaining time until expiration in seconds
   * Used for countdown timer display (mm:ss format)
   */
  remainingTimeInSeconds: number;

  /**
   * Optional URL of an image detected in the content
   * If present, the UI should render a thumbnail
   */
  imageUrl?: {
    primaryUrl: string;
    fallbackUrl?: string;
  } | null;
}

/**
 * Request payload for posting a new spark
 */
export interface PostSparkRequest {
  /**
   * Spark content text to post
   */
  content: string;
}

/**
 * Request payload for adding fuel to a spark
 */
export interface AddFuelRequest {
  /**
   * Target spark ID to add fuel
   */
  sparkId: string;
}
