/**
 * Post Reply UseCase Hook
 *
 * Custom hook for posting a reply to a bonfire using SWR Mutation.
 * Depends on ISparkRepository (Domain Interface) following DIP.
 */

import useSWRMutation from "swr/mutation";
import type { Spark } from "@/domain/model/spark";
import type {
  ISparkRepository,
  PostReplyRequest,
} from "@/domain/repository/sparkRepository";
import type { ILogger } from "@/usecase/ports/ILogger";
import { LOG_EVENTS } from "@/domain/constants";

/**
 * SWR key generator for reply mutation
 * @param bonfireId - The bonfire ID
 * @returns SWR mutation key string
 */
const getReplyKey = (bonfireId: string) => `/bonfire/${bonfireId}/reply`;

/**
 * UseCase Hook for posting a reply to a bonfire (Mutation).
 * @param bonfireId - The bonfire ID to reply to
 * @param fieldId - The field ID (Community)
 * @param repository - Repository implementation (injected from outside)
 * @param logger - Logger implementation (injected from outside)
 * @returns Mutation state and trigger function
 */
export const usePostReply = (
  bonfireId: string,
  fieldId: string,
  repository: ISparkRepository,
  logger: ILogger,
) => {
  const { trigger, isMutating, error } = useSWRMutation<
    Spark,
    Error,
    string,
    string // content only, bonfireId and fieldId come from hook arguments
  >(
    getReplyKey(bonfireId),
    async (_key: string, { arg: content }: { arg: string }) => {
      try {
        logger.info("Posting reply to bonfire", {
          event: LOG_EVENTS.SPARK.POST_START,
          bonfireId,
          contentLength: content.length,
          fieldId,
        });
        const request: PostReplyRequest = {
          content,
          parentBonfireId: bonfireId,
          fieldId,
        };
        const createdSpark = await repository.postReply(request);
        logger.info("Successfully posted reply", {
          event: LOG_EVENTS.SPARK.POST_SUCCESS,
          sparkId: createdSpark.id,
          bonfireId,
        });
        return createdSpark;
      } catch (error_) {
        logger.error(error_, {
          event: LOG_EVENTS.SPARK.POST_ERROR,
          context: "usePostReply",
          bonfireId,
          fieldId,
        });
        throw error_;
      }
    },
  );

  return {
    postReply: trigger,
    isPosting: isMutating,
    error: error ?? null,
  };
};
