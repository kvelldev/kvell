/**
 * Spark Domain Model
 *
 * Represents a single spark (種火) - the core unit of all topics in Kvell.
 */

/**
 *
 */
export interface Spark {
  id: string;
  content: string;
  createdAt: string;
}

/**
 *
 */
export interface PostSparkRequest {
  content: string;
}
