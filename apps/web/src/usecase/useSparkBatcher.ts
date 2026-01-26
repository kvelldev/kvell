import { useState, useEffect, useRef, useCallback } from "react";
import type { Spark } from "@/domain/model/spark";
import type { TimelineEvent } from "@/domain/model/timelineEvent";

const BATCH_INTERVAL_MS = 200;

export const useSparkBatcher = (onBonfirePromoted?: () => void) => {
  const [sparks, setSparks] = useState<Spark[]>([]);
  const eventBuffer = useRef<TimelineEvent[]>([]);

  // Function to receive events from external source
  const pushEvent = useCallback((event: TimelineEvent) => {
    eventBuffer.current.push(event);
  }, []);

  useEffect(() => {
    const processBatch = () => {
      if (eventBuffer.current.length === 0) return;

      const events = [...eventBuffer.current];
      eventBuffer.current = []; // Clear buffer

      setSparks((currentSparks) => {
        const updatedSparks = [...currentSparks];
        let bonfirePromoted = false;

        for (const event of events) {
          if (event.type === "spark_posted") {
            const newSpark = event.data;
            // Deduplication
            if (!updatedSparks.some((s) => s.id === newSpark.id)) {
              updatedSparks.push(newSpark);
            }
          } else {
            // Must be "spark_updated"
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
        }

        if (bonfirePromoted && onBonfirePromoted) {
          // Trigger callback
          setTimeout(onBonfirePromoted, 0);
        }

        return updatedSparks;
      });
    };

    const timer = setInterval(processBatch, BATCH_INTERVAL_MS);
    return () => {
      clearInterval(timer);
    };
  }, [onBonfirePromoted]);

  return { sparks, pushEvent };
};
