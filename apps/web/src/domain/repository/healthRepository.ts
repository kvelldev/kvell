/**
 * Health Repository Interface
 *
 * Repository abstraction for health check operations (DIP).
 * This interface is defined in the domain layer and implemented in the adapter layer.
 */

import type { HealthMessage } from "@/domain/model/health";

/**
 * Repository interface for health check operations.
 * Adapter layer must implement this interface.
 */
export interface IHealthRepository {
  /**
   * Save a health check message to the database.
   * @param message - The message to save
   * @returns The saved health message with ID and timestamp
   */
  saveMessage(message: string): Promise<HealthMessage>;

  /**
   * Get the latest health check message from the database.
   * @returns The latest health message, or null if none exists
   */
  getLatest(): Promise<HealthMessage | null>;
}
