/**
 * ReadMarker Repository Interface (DIP)
 *
 * Abstract definition of data access operations for persisting
 * the user's last read position in a bonfire.
 * Implementation uses LocalStorage for client-side persistence.
 */

/**
 * ReadMarker Repository Interface
 */
export interface IReadMarkerRepository {
  /**
   * Save the last read spark ID for a bonfire.
   * @param bonfireId - The bonfire ID
   * @param sparkId - The last read spark ID
   */
  saveLastRead(bonfireId: string, sparkId: string): void;

  /**
   * Get the last read spark ID for a bonfire.
   * @param bonfireId - The bonfire ID
   * @returns The last read spark ID, or null if not found
   */
  getLastRead(bonfireId: string): string | null;

  /**
   * Clear the last read position for a bonfire.
   * @param bonfireId - The bonfire ID
   */
  clearLastRead(bonfireId: string): void;
}
