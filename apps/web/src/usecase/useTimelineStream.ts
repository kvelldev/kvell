/**
 * Timeline Stream UseCase
 *
 * Business logic for real-time timeline spark streaming.
 * Manages WebSocket connection, spark accumulation, deduplication, TTL cleanup,
 * and temperature calculation for UI rendering.
 */

import { useEffect, useState } from "react";
import type { Spark, SparkViewModel } from "@/domain/model/spark";
import type { ITimelineRepository } from "@/domain/repository/timelineRepository";
import { computeSparkViewModel } from "@/domain/service/sparkService";

/**
 * Update interval for temperature recalculation and TTL cleanup
 * Run every second for immediate removal of expired sparks and temperature updates
 */
const UPDATE_INTERVAL_MS = 1000;

/**
 * Compute ViewModels from raw sparks by adding temperature state and remaining time
 * @param sparks - Raw spark data from repository
 * @returns Spark ViewModels with computed temperature and countdown timer
 */
const computeViewModels = (sparks: Spark[]): SparkViewModel[] => {
  return sparks.map(computeSparkViewModel);
};

/**
 * Timeline Stream Custom Hook
 * @param repository - Timeline repository implementation (DIP)
 * @returns Object containing current spark ViewModels and connection error state
 */
export const useTimelineStream = (repository: ITimelineRepository) => {
  const [sparks, setSparks] = useState<Spark[]>([]);
  const [viewModels, setViewModels] = useState<SparkViewModel[]>([]);
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

    // 2. Setup periodic temperature recalculation and TTL cleanup
    const updateTimer = setInterval(() => {
      const now = Date.now();

      setSparks((previous) => {
        // Filter out expired sparks
        const aliveSparks = previous.filter((spark) => {
          const expirationTime = new Date(spark.decayAt).getTime();
          return now < expirationTime;
        });

        return aliveSparks;
      });
    }, UPDATE_INTERVAL_MS);

    // 3. Cleanup on unmount
    return () => {
      disconnect();
      clearInterval(updateTimer);
    };
  }, [repository]);

  // 4. Recompute ViewModels whenever sparks change or timer ticks
  useEffect(() => {
    const timer = setInterval(() => {
      setViewModels(computeViewModels(sparks));
    }, UPDATE_INTERVAL_MS);

    // Initial computation
    setViewModels(computeViewModels(sparks));

    return () => {
      clearInterval(timer);
    };
  }, [sparks]);

  return { sparks: viewModels, hasError };
};
