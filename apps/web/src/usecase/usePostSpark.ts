/**
 * Post Spark UseCase Hook
 *
 * Custom hook for posting a new spark using SWR Mutation.
 * Depends on ISparkRepository (Domain Interface) following DIP.
 */

import useSWRMutation from "swr/mutation";
import type { PostSparkRequest, Spark } from "@/domain/model/spark";
import type { ISparkRepository } from "@/domain/repository/sparkRepository";
import type { ILogger } from "@/usecase/ports/ILogger";
import { SWR_KEYS } from "@/usecase/constants";
import { LOG_EVENTS } from "@/domain/constants";

/**
 * UseCase Hook for posting a spark (Mutation).
 * @param repository - Repository implementation (injected from outside)
 * @param logger - Logger implementation (injected from outside)
 * @param fieldId - Current field ID (context)
 * @returns Mutation state and trigger function
 */
export const usePostSpark = (
  repository: ISparkRepository,
  logger: ILogger,
  fieldId: string,
) => {
  const { trigger, isMutating, error } = useSWRMutation<
    Spark,
    Error,
    string,
    Omit<PostSparkRequest, "fieldId">
  >(
    SWR_KEYS.SPARK_POST,
    async (
      _key: string,
      { arg }: { arg: Omit<PostSparkRequest, "fieldId"> },
    ) => {
      try {
        logger.info("Posting spark", {
          event: LOG_EVENTS.SPARK.POST_START,
          contentLength: arg.content.length,
          fieldId,
        });
        const createdSpark = await repository.postSpark({
          ...arg,
          fieldId,
        });
        logger.info("Successfully posted spark", {
          event: LOG_EVENTS.SPARK.POST_SUCCESS,
          sparkId: createdSpark.id,
        });
        return createdSpark;
      } catch (error_) {
        logger.error(error_, {
          event: LOG_EVENTS.SPARK.POST_ERROR,
          context: "usePostSpark",
          contentLength: arg.content.length,
          fieldId,
        });
        throw error_;
      }
    },
  );

  return {
    postSpark: trigger,
    isPosting: isMutating,
    error: error ?? null,
  };
};
