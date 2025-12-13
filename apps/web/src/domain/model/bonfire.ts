/**
 * Bonfire Domain Model
 *
 * Represents a promoted spark (焚き火) that appears in the Bonfire Area.
 */

/**
 * Bonfire interface
 */
export interface Bonfire {
  /**
   * Unique identifier (same as original spark_id)
   */
  id: string;

  /**
   * Reference to the original spark ID
   */
  sparkId: string;

  /**
   * Bonfire content text
   */
  content: string;

  /**
   * Number of unique users engaged at promotion
   */
  uniqueUserCount: number;

  /**
   * Heat score at promotion
   */
  heatScore: number;

  /**
   * ISO timestamp when the bonfire was created (promoted)
   */
  createdAt: string;

  /**
   * ISO timestamp when the bonfire decays
   */
  decayAt: string;
}

/**
 * Bonfire List Response
 */
export interface BonfireList {
  bonfires: Bonfire[];
  count: number;
}
