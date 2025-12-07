/**
 * Spark Domain Model
 *
 * Represents a single spark (種火) - the core unit of all topics in Kvell.
 */

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
   * ISO timestamp until which the spark remains visible (TTL expiration)
   */
  visibleUntil: string;
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
