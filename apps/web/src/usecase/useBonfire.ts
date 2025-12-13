/**
 * useBonfire Hook
 *
 * Manages bonfire data fetching using SWR.
 */

import useSWR from "swr";
import { IBonfireRepository } from "@/domain/repository/bonfireRepository";
import { BonfireList } from "@/domain/model/bonfire";

// SWR key for active bonfires
const BONFIRE_FETCH_KEY = "/bonfire/active";

export const useBonfire = (repository: IBonfireRepository) => {
  // Use SWR for data fetching and state management
  const { data, error, isLoading, mutate } = useSWR<BonfireList, Error>(
    BONFIRE_FETCH_KEY,
    () => repository.getActiveBonfires(),
  );

  return {
    bonfires: data?.bonfires ?? [], // Return empty list if no data
    count: data?.count ?? 0,
    isLoading,
    error,
    refetch: mutate, // Expose mutate as refetch
  };
};
