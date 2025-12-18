/**
 * UseReadMarker Hook
 *
 * Custom hook for managing the "read up to here" marker functionality.
 * Implements High Water Mark pattern with fixed-position marker (LINE/Discord style).
 *
 * Key concepts:
 * - displayMarkerSparkId: Fixed marker position for current session (does not move while scrolling)
 * - sessionHighWaterIndex: Tracks the furthest scroll position (updated on scroll, saved on leave)
 */

import { useCallback, useEffect, useRef, useState } from "react";
import type { IReadMarkerRepository } from "@/domain/repository/readMarkerRepository";

/**
 * Return type for useReadMarker hook
 */
interface UseReadMarkerResult {
  /**
   * Marker display position SparkID (fixed during session, does not move)
   * Used by ReplyTimeline to show "read up to here" marker
   */
  displayMarkerSparkId: string | null;

  /**
   * Report visible scroll position (sparkId and index)
   * Called by ReplyTimeline when visible range changes
   * Only updates high water mark if index is greater than current (forward only)
   */
  reportVisiblePosition: (sparkId: string, index: number) => void;

  /**
   * Commit high water mark to storage
   * Called on page leave (unmount or close)
   * Only saves if session high water > persisted high water (no backward)
   */
  commitToStorage: () => void;

  /**
   * Clear the read marker
   */
  clearReadMarker: () => void;
}

/**
 * Options for useReadMarker hook
 */
interface UseReadMarkerOptions {
  /**
   * Function to get the persisted index for comparison
   * Called during commitToStorage to check if we should save
   */
  getPersistedIndex?: () => number;
}

/**
 * Custom hook for managing read markers in bonfires.
 * Implements High Water Mark pattern with LINE/Discord-style fixed marker.
 * @param bonfireId - The bonfire ID to track reading position
 * @param repository - Repository implementation (injected from outside)
 * @param options - Optional configuration for persisted index lookup
 * @returns Read marker state and methods
 */
export const useReadMarker = (
  bonfireId: string,
  repository: IReadMarkerRepository,
  options?: UseReadMarkerOptions,
): UseReadMarkerResult => {
  // Display marker position (fixed during session)
  // Initialize lazily to ensure it's available for first render (correct initial scroll position)
  const [displayMarkerSparkId, setDisplayMarkerSparkId] = useState<
    string | null
  >(() => {
    return repository.getLastRead(bonfireId);
  });

  // Session high water mark (furthest scroll position)
  const sessionHighWaterIndexRef = useRef<number>(-1);

  // Pending commit spark ID (to be saved on leave)
  const pendingCommitSparkIdRef = useRef<string | null>(null);

  // Keep options in ref to avoid stale closure
  const optionsRef = useRef(options);
  optionsRef.current = options;

  // Keep repository and bonfireId in refs for cleanup
  const repositoryRef = useRef(repository);
  repositoryRef.current = repository;
  const bonfireIdRef = useRef(bonfireId);
  bonfireIdRef.current = bonfireId;

  // Load last read position on mount
  useEffect(() => {
    const savedSparkId = repository.getLastRead(bonfireId);
    setDisplayMarkerSparkId(savedSparkId);

    // Reset session state when bonfire changes
    sessionHighWaterIndexRef.current = -1;
    pendingCommitSparkIdRef.current = null;
  }, [bonfireId, repository]);

  // Report visible scroll position
  const reportVisiblePosition = useCallback(
    (sparkId: string, index: number) => {
      // Only update if moving forward (high water mark pattern)
      if (index > sessionHighWaterIndexRef.current) {
        sessionHighWaterIndexRef.current = index;
        pendingCommitSparkIdRef.current = sparkId;
      }
    },
    [],
  );

  // Commit to storage (called on page leave)
  const commitToStorage = useCallback(() => {
    const pendingSparkId = pendingCommitSparkIdRef.current;
    if (!pendingSparkId) return;

    // Get persisted index for comparison
    const persistedIndex = optionsRef.current?.getPersistedIndex?.() ?? -1;

    // Only save if we've scrolled further than the persisted position
    if (sessionHighWaterIndexRef.current > persistedIndex) {
      repositoryRef.current.saveLastRead(bonfireIdRef.current, pendingSparkId);
    }
  }, []);

  // Clear the read marker
  const clearReadMarker = useCallback(() => {
    repository.clearLastRead(bonfireId);
    setDisplayMarkerSparkId(null);
    sessionHighWaterIndexRef.current = -1;
    pendingCommitSparkIdRef.current = null;
  }, [bonfireId, repository]);

  return {
    displayMarkerSparkId,
    reportVisiblePosition,
    commitToStorage,
    clearReadMarker,
  };
};
