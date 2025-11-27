/**
 * Health Check Domain Model
 *
 * Domain layer types for health check operations.
 */

/**
 *
 */
export interface HealthMessage {
  id: string;
  message: string;
  createdAt: string;
}
