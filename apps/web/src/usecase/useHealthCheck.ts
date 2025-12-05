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
import type { ILogger } from "@/usecase/ports/ILogger";
import { SWR_KEYS } from "@/usecase/constants";
import { LOG_EVENTS } from "@/domain/constants";

/**
 * UseCase Hook for fetching the latest health message (SWR).
 * @param repository - Repository implementation (injected from outside)
 * @param logger - Logger implementation (injected from outside)
 * @returns SWR state for latest health message
 */
export const useFetchLatestHealthMessage = (
  repository: IHealthRepository,
  logger: ILogger,
) => {
  const { data, error, isLoading, mutate } = useSWR<
    HealthMessage | null,
    Error
  >(
    SWR_KEYS.HEALTH_LATEST,
    async () => {
      try {
        logger.info("Fetching latest health message", {
          event: LOG_EVENTS.HEALTH_CHECK.FETCH_START,
        });
        const result = await repository.getLatest();
        logger.info("Successfully fetched latest health message", {
          event: LOG_EVENTS.HEALTH_CHECK.FETCH_SUCCESS,
          hasData: !!result,
        });
        return result;
      } catch (error_) {
        logger.error(error_, {
          event: LOG_EVENTS.HEALTH_CHECK.FETCH_ERROR,
          context: "useFetchLatestHealthMessage",
        });
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
 * @param logger - Logger implementation (injected from outside)
 * @returns Mutation state and trigger function
 */
export const useSaveHealthMessage = (
  repository: IHealthRepository,
  logger: ILogger,
) => {
  const { trigger, isMutating, error } = useSWRMutation<
    HealthMessage,
    Error,
    string,
    string
  >(
    SWR_KEYS.HEALTH_LATEST,
    async (_key: string, { arg }: { arg: string }) => {
      try {
        logger.info("Saving health message", {
          event: LOG_EVENTS.HEALTH_CHECK.SAVE_START,
          message: arg,
        });
        const savedMessage = await repository.saveMessage(arg);
        logger.info("Successfully saved health message", {
          event: LOG_EVENTS.HEALTH_CHECK.SAVE_SUCCESS,
          id: savedMessage.id,
        });
        return savedMessage;
      } catch (error_) {
        logger.error(error_, {
          event: LOG_EVENTS.HEALTH_CHECK.SAVE_ERROR,
          context: "useSaveHealthMessage",
          message: arg,
        });
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
