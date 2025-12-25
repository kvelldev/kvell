/**
 * UseBonfireRoom Hook
 *
 * Custom hook for managing WebSocket connection to a bonfire room.
 * Handles real-time spark (reply) streaming and bonfire lifecycle events.
 */

import { useCallback, useEffect, useState } from "react";
import type { Spark } from "@/domain/model/spark";
import type {
  IBonfireRoomRepository,
  ParsedBonfireMessage,
} from "@/domain/repository/bonfireRoomRepository";
import {
  useResilientWebSocket,
  type ConnectionStatus,
} from "./useResilientConnection";

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
   * Connection status for UI feedback (Toast)
   */
  status: ConnectionStatus;

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

  // Reset state when bonfireId changes
  useEffect(() => {
    setSparks([]);
    setIsDecayed(false);
  }, [bonfireId]);

  // Handle incoming messages
  const handleMessage = useCallback((event: ParsedBonfireMessage) => {
    if (event.type === "spark") {
      const spark = event.data;
      setSparks((previous) => {
        const exists = previous.some((s) => s.id === spark.id);
        if (exists) return previous;
        return [...previous, spark];
      });
    } else {
      // event.type === "bonfire_event"
      if (event.data.eventType === "decayed") {
        setIsDecayed(true);
      }
    }
  }, []);

  // Use the resilient WebSocket hook
  const status = useResilientWebSocket(
    repository.getConnectionUrl(bonfireId),
    (message) => repository.parseMessage(message),
    handleMessage,
  );

  // Add a spark to the local list (for optimistic updates)
  const addLocalSpark = useCallback((spark: Spark) => {
    setSparks((previous) => {
      const exists = previous.some((s) => s.id === spark.id);
      if (exists) return previous;
      return [...previous, spark];
    });
  }, []);

  return {
    sparks,
    isDecayed,
    status,
    addLocalSpark,
  };
};
