/**
 * LocalStorage ReadMarker Repository Implementation
 *
 * Adapter layer implementation of IReadMarkerRepository.
 * Persists the user's last read position in a bonfire using LocalStorage.
 */

import type { IReadMarkerRepository } from "@/domain/repository/readMarkerRepository";

/**
 * LocalStorage key prefix for read markers
 */
const STORAGE_KEY_PREFIX = "kvell:readMarker:";

/**
 * LocalStorage ReadMarker Repository Implementation
 */
class LocalStorageReadMarkerRepositoryImpl implements IReadMarkerRepository {
  private getStorageKey(bonfireId: string): string {
    return `${STORAGE_KEY_PREFIX}${bonfireId}`;
  }

  saveLastRead(bonfireId: string, sparkId: string): void {
    try {
      localStorage.setItem(this.getStorageKey(bonfireId), sparkId);
    } catch (error) {
      // LocalStorage might be full or disabled
      console.warn("Failed to save read marker:", error);
    }
  }

  getLastRead(bonfireId: string): string | null {
    try {
      return localStorage.getItem(this.getStorageKey(bonfireId));
    } catch (error) {
      console.warn("Failed to get read marker:", error);
      return null;
    }
  }

  clearLastRead(bonfireId: string): void {
    try {
      localStorage.removeItem(this.getStorageKey(bonfireId));
    } catch (error) {
      console.warn("Failed to clear read marker:", error);
    }
  }
}

/**
 * Singleton instance of LocalStorage ReadMarker Repository
 */
export const localStorageReadMarkerRepository: IReadMarkerRepository =
  new LocalStorageReadMarkerRepositoryImpl();
