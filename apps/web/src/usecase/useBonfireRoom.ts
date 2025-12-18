/**
 * UseBonfireRoom Hook
 *
 * Custom hook for managing WebSocket connection to a bonfire room.
 * Handles real-time spark (reply) streaming and bonfire lifecycle events.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import type { Spark } from "@/domain/model/spark";
import type { BonfireEvent } from "@/domain/model/bonfireEvent";
import type { IBonfireRoomRepository } from "@/domain/repository/bonfireRoomRepository";

/**
 * Return type for useBonfireRoom hook
 */
interface UseBonfireRoomResult {
  /**
   * Array of sparks (replies) in the bonfire, sorted by createdAt (oldest first)
   */
  sparks: Spark[];

  /**
   * Whether the bonfire has decayed (鎮火)
   */
  isDecayed: boolean;

  /**
   * Whether an error occurred with the WebSocket connection
   */
  hasError: boolean;

  /**
   * Add a spark to the local list (for optimistic updates)
   */
  addLocalSpark: (spark: Spark) => void;
}

/**
 * Custom hook for managing bonfire room WebSocket connection.
 * @param bonfireId - The bonfire ID to connect to
 * @param repository - Repository implementation (injected from outside)
 * @returns Bonfire room state and methods
 */
export const useBonfireRoom = (
  bonfireId: string,
  repository: IBonfireRoomRepository,
): UseBonfireRoomResult => {
  const [sparks, setSparks] = useState<Spark[]>([]);
  const [isDecayed, setIsDecayed] = useState(false);
  const [hasError, setHasError] = useState(false);

  // Use ref to avoid stale closure in callbacks
  const sparksRef = useRef(sparks);
  sparksRef.current = sparks;

  // Add a spark to the local list (for optimistic updates after posting)
  // Includes duplicate check to handle race conditions with WebSocket
  const addLocalSpark = useCallback((spark: Spark) => {
    setSparks((previous) => {
      const exists = previous.some((s) => s.id === spark.id);
      if (exists) return previous;
      return [...previous, spark];
    });
  }, []);

  useEffect(() => {
    // Reset state when connecting to a new bonfire
    setSparks([]);
    setIsDecayed(false);
    setHasError(false);

    const handleSpark = (spark: Spark) => {
      // Add spark if it doesn't already exist (avoid duplicates from optimistic updates)
      setSparks((previous) => {
        const exists = previous.some((s) => s.id === spark.id);
        if (exists) return previous;
        return [...previous, spark];
      });
    };

    const handleBonfireEvent = (event: BonfireEvent) => {
      if (event.eventType === "decayed") {
        setIsDecayed(true);
      }
      // 'extended' event doesn't require UI state change for now
    };

    const handleError = () => {
      setHasError(true);
    };

    const disconnect = repository.connect(bonfireId, {
      onSpark: handleSpark,
      onBonfireEvent: handleBonfireEvent,
      onError: handleError,
    });

    return disconnect;
  }, [bonfireId, repository]);

  return {
    sparks,
    isDecayed,
    hasError,
    addLocalSpark,
  };
};
