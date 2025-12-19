/**
 * Timeline Stream UseCase
 *
 * Business logic for real-time timeline spark streaming.
 * Manages WebSocket connection, spark accumulation, deduplication, TTL cleanup,
 * and temperature calculation for UI rendering.
 *
 * Implements batching for incoming events to reduce render frequency.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import type { Spark, SparkViewModel } from "@/domain/model/spark";
import type { ITimelineRepository } from "@/domain/repository/timelineRepository";
import type { TimelineEvent } from "@/domain/model/timelineEvent";
import { computeSparkViewModel } from "@/domain/service/sparkService";

/**
 * Update interval for temperature recalculation and TTL cleanup
 * Run every second for immediate removal of expired sparks and temperature updates
 */
const UPDATE_INTERVAL_MS = 1000;

/**
 * Batch processing interval in milliseconds.
 * Incoming WebSocket events are buffered and processed in chunks to prevent UI jank.
 */
const BATCH_INTERVAL_MS = 200;

/**
 * Compute ViewModels from raw sparks by adding temperature state and remaining time
 * @param sparks - Raw spark data from repository
 * @returns Spark ViewModels with computed temperature and countdown timer
 */
const computeViewModels = (sparks: Spark[]): SparkViewModel[] => {
  return sparks.map(computeSparkViewModel);
};

interface UseTimelineStreamProps {
  repository: ITimelineRepository;
  onBonfirePromoted?: () => void;
}

/**
 * Timeline Stream Custom Hook
 * @param repository - Timeline repository implementation (DIP)
 * @param onBonfirePromoted - Callback triggers when a spark is promoted to Bonfire
 * @returns Object containing current spark ViewModels and connection error state
 */
export const useTimelineStream = ({
  repository,
  onBonfirePromoted,
}: UseTimelineStreamProps) => {
  const [sparks, setSparks] = useState<Spark[]>([]);
  const [viewModels, setViewModels] = useState<SparkViewModel[]>([]);
  const [hasError, setHasError] = useState(false);

  // Buffer for incoming events to be processed in batch
  const eventBuffer = useRef<TimelineEvent[]>([]);

  // Batch process incoming events
  useEffect(() => {
    const processBatch = () => {
      if (eventBuffer.current.length === 0) return;

      const events = [...eventBuffer.current];
      eventBuffer.current = []; // Clear buffer

      setSparks((currentSparks) => {
        let updatedSparks = [...currentSparks];
        let bonfirePromoted = false;

        events.forEach((event) => {
          if (event.type === "spark_posted") {
            const newSpark = event.data;
            // Deduplication
            if (!updatedSparks.some((s) => s.id === newSpark.id)) {
              updatedSparks.push(newSpark);
            }
          } else if (event.type === "spark_updated") {
            const { spark_id, level, decay_at } = event;

            // Find spark to update
            const sparkIndex = updatedSparks.findIndex(
              (s) => s.id === spark_id,
            );
            if (sparkIndex !== -1) {
              if (level === "bonfire") {
                // Remove from timeline if promoted to Bonfire
                updatedSparks.splice(sparkIndex, 1);
                bonfirePromoted = true;
              } else {
                // Update properties (e.g. extension to Kindling)
                updatedSparks[sparkIndex] = {
                  ...updatedSparks[sparkIndex],
                  decayAt: decay_at,
                };
              }
            }
          }
        });

        if (bonfirePromoted && onBonfirePromoted) {
          // Trigger callback (outside check to avoid state update loops if possible,
          // but here needs setTimeout to break render cycle potentially)
          setTimeout(onBonfirePromoted, 0);
        }

        return updatedSparks;
      });
    };

    const batchTimer = setInterval(processBatch, BATCH_INTERVAL_MS);
    return () => clearInterval(batchTimer);
  }, [onBonfirePromoted]);

  useEffect(() => {
    // Reset error state on new connection attempt
    setHasError(false);

    // 1. Establish WebSocket connection
    const disconnect = repository.connect(
      (event) => {
        // Push to buffer instead of updating state directly
        eventBuffer.current.push(event);
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

        // Optimization: return same reference if nothing changed
        if (aliveSparks.length === previous.length) {
          return previous;
        }

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
  // Logic remains same: periodic update for countdown
  useEffect(() => {
    // Immediate update when sparks change
    setViewModels(computeViewModels(sparks));

    const timer = setInterval(() => {
      setViewModels((prevViewModels) => {
        // Recompute to update time remaining
        // We use the same sparks state unless it changed
        return computeViewModels(sparks);
      });
    }, UPDATE_INTERVAL_MS);

    return () => clearInterval(timer);
  }, [sparks]);

  return { sparks: viewModels, hasError };
};
