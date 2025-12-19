/**
 * useBonfire Hook
 *
 * Manages bonfire data fetching using SWR.
 */

import useSWR from "swr";
import { useMemo } from "react";
import { IBonfireRepository } from "@/domain/repository/bonfireRepository";
import { BonfireList, BonfireViewModel } from "@/domain/model/bonfire";
import { detectSparkImage } from "@/domain/service/sparkUrlService";

// SWR key for active bonfires
const BONFIRE_FETCH_KEY = "/bonfire/active";

export const useBonfire = (repository: IBonfireRepository) => {
  // Use SWR for data fetching and state management
  const { data, error, isLoading, mutate } = useSWR<BonfireList, Error>(
    BONFIRE_FETCH_KEY,
    () => repository.getActiveBonfires(),
  );

  // Transform to ViewModel (derive state)
  const bonfires: BonfireViewModel[] = useMemo(() => {
    if (!data?.bonfires) return [];
    return data.bonfires.map((bonfire) => ({
      ...bonfire,
      imageUrl: detectSparkImage(bonfire.content),
    }));
  }, [data?.bonfires]);

  return {
    bonfires,
    count: data?.count ?? 0,
    isLoading,
    error,
    refetch: mutate, // Expose mutate as refetch
  };
};
