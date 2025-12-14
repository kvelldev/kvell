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
   * @returns Promise resolving to BonfireList
   */
  getActiveBonfires(): Promise<BonfireList>;
}
