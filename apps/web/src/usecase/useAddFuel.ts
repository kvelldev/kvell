/**
 * Add Fuel UseCase Hook
 *
 * Custom hook for adding fuel to a spark.
 * Triggers haptic feedback and ignite effect without displaying fuel count.
 */

import useSWRMutation from "swr/mutation";
import type { AddFuelRequest } from "@/domain/model/spark";
import type { ISparkRepository } from "@/domain/repository/sparkRepository";
import type { ILogger } from "@/usecase/ports/ILogger";
import { SWR_KEYS } from "@/usecase/constants";
import { LOG_EVENTS } from "@/domain/constants";

/**
 * UseCase Hook for adding fuel to a spark (Mutation).
 * @param repository - Repository implementation (injected from outside)
 * @param logger - Logger implementation (injected from outside)
 * @returns Mutation state, trigger function, and haptic support status
 */
export const useAddFuel = (repository: ISparkRepository, logger: ILogger) => {
  const { trigger, isMutating, error } = useSWRMutation<
    null,
    Error,
    string,
    AddFuelRequest
  >(
    SWR_KEYS.ADD_FUEL,
    async (_key: string, { arg }: { arg: AddFuelRequest }) => {
      try {
        logger.info("Adding fuel to spark", {
          event: LOG_EVENTS.ADD_FUEL.START,
          sparkId: arg.sparkId,
        });

        // Send fuel event to backend (no fuel count returned)
        await repository.addFuel(arg);

        logger.info("Successfully added fuel", {
          event: LOG_EVENTS.ADD_FUEL.SUCCESS,
          sparkId: arg.sparkId,
        });

        return null;
      } catch (error_) {
        logger.error(error_, {
          event: LOG_EVENTS.ADD_FUEL.ERROR,
          context: "useAddFuel",
          sparkId: arg.sparkId,
        });
        throw error_;
      }
    },
  );

  return {
    addFuel: trigger,
    isAdding: isMutating,
    error: error ?? null,
  };
};
