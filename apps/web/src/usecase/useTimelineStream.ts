/**
 * Timeline Stream UseCase
 *
 * Business logic for real-time timeline spark streaming.
 * Manages WebSocket connection, spark accumulation, deduplication, and TTL cleanup.
 */

import { useEffect, useState } from "react";
import type { Spark } from "@/domain/model/spark";
import type { ITimelineRepository } from "@/domain/repository/timelineRepository";

/**
 * Cleanup interval for removing expired sparks
 * Run cleanup every second for immediate removal of expired sparks
 */
const CLEANUP_INTERVAL_MS = 1000;

/**
 * Timeline Stream Custom Hook
 * @param repository - Timeline repository implementation (DIP)
 * @returns Object containing current sparks array and connection error state
 */
export const useTimelineStream = (repository: ITimelineRepository) => {
  const [sparks, setSparks] = useState<Spark[]>([]);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    // Reset error state on new connection attempt
    setHasError(false);

    // 1. Establish WebSocket connection
    const disconnect = repository.connect(
      (newSpark) => {
        setSparks((previous) => {
          // Deduplication: Check if spark with same ID already exists
          const exists = previous.some((spark) => spark.id === newSpark.id);
          if (exists) {
            return previous;
          }

          // Append new spark to the end (ascending order for chat-like display)
          return [...previous, newSpark];
        });
      },
      () => {
        // Error callback
        setHasError(true);
      },
    );

    // 2. Setup periodic TTL cleanup based on visibleUntil
    const cleanupTimer = setInterval(() => {
      const now = Date.now();

      setSparks((previous) =>
        previous.filter((spark) => {
          const expirationTime = new Date(spark.visibleUntil).getTime();

          // Keep spark if it hasn't exceeded its visibleUntil time
          return now < expirationTime;
        }),
      );
    }, CLEANUP_INTERVAL_MS);

    // 3. Cleanup on unmount
    return () => {
      disconnect();
      clearInterval(cleanupTimer);
    };
  }, [repository]);

  return { sparks, hasError };
};
