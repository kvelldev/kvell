/**
 * Bonfire Repository Interface (DIP)
 *
 * Defines the contract for fetching bonfire data.
 */

import { BonfireList } from "@/domain/model/bonfire";

/**
 * Bonfire Repository Interface
 *
 * Defines the contract for fetching bonfire data.
 */
export interface IBonfireRepository {
  /**
   * Get all active (non-decayed) bonfires
   * @param fieldId - The field (community) ID
   * @returns Promise resolving to BonfireList
   */
  getActiveBonfires(fieldId?: string): Promise<BonfireList>;
}
