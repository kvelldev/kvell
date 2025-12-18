/**
 * BonfireEvent Domain Model
 *
 * Represents events that occur during a bonfire's lifecycle.
 * These events are streamed via WebSocket from the backend.
 */

/**
 * Types of bonfire lifecycle events
 */
export type BonfireEventType = "decayed" | "extended";

/**
 * BonfireEvent interface
 * Corresponds to backend BonfireEvent schema
 */
export interface BonfireEvent {
  /**
   * Event type: 'decayed' when bonfire expires, 'extended' when lifespan is extended
   */
  eventType: BonfireEventType;

  /**
   * ID of the bonfire this event relates to
   */
  bonfireId: string;

  /**
   * Optional message describing the event
   */
  message?: string;
}
