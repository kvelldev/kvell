/**
 * Health Check UseCase Hooks
 *
 * Custom hooks for health check operations using SWR.
 * Depends on IHealthRepository (Domain Interface) following DIP.
 */

import useSWR from "swr";
import useSWRMutation from "swr/mutation";
import type { HealthMessage } from "@/domain/model/health";
import type { IHealthRepository } from "@/domain/repository/healthRepository";
import { SWR_KEYS } from "@/usecase/constants";
import { useLogger } from "@/usecase/ports/LoggerContext";

/**
 * UseCase Hook for fetching the latest health message (SWR).
 * @param repository - Repository implementation (injected from outside)
 * @returns SWR state for latest health message
 */
export const useFetchLatestHealthMessage = (repository: IHealthRepository) => {
  const logger = useLogger();

  const { data, error, isLoading, mutate } = useSWR<
    HealthMessage | null,
    Error
  >(
    SWR_KEYS.HEALTH_LATEST,
    async () => {
      try {
        logger.info("Fetching latest health message");
        const result = await repository.getLatest();
        logger.info("Successfully fetched latest health message", {
          hasData: !!result,
        });
        return result;
      } catch (error_) {
        logger.error(error_, { context: "useFetchLatestHealthMessage" });
        throw error_;
      }
    },
    {
      // Don't revalidate on focus/reconnect for this health check demo
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    },
  );

  return {
    message: data ?? null,
    isLoading,
    isError: !!error,
    error,
    refetch: mutate,
  };
};

/**
 * UseCase Hook for saving a health message (Mutation).
 * @param repository - Repository implementation (injected from outside)
 * @returns Mutation state and trigger function
 */
export const useSaveHealthMessage = (repository: IHealthRepository) => {
  const logger = useLogger();

  const { trigger, isMutating, error } = useSWRMutation<
    HealthMessage,
    Error,
    string,
    string
  >(
    SWR_KEYS.HEALTH_LATEST,
    async (_key: string, { arg }: { arg: string }) => {
      try {
        logger.info("Saving health message", { message: arg });
        const savedMessage = await repository.saveMessage(arg);
        logger.info("Successfully saved health message", {
          id: savedMessage.id,
        });
        return savedMessage;
      } catch (error_) {
        logger.error(error_, { context: "useSaveHealthMessage", message: arg });
        throw error_;
      }
    },
    {
      // Automatically update the cache after successful mutation
      populateCache: true,
      revalidate: false,
    },
  );

  return {
    saveMessage: trigger,
    isSaving: isMutating,
    error: error ?? null,
  };
};
