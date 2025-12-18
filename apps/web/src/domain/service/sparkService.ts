/**
 * Spark Domain Service
 *
 * Pure business logic for spark-related calculations.
 * No dependencies on UI or infrastructure.
 */

import type { Spark, SparkViewModel } from "@/domain/model/spark";
import { COOLING_THRESHOLD_RATIO } from "@/domain/constants";

/**
 * Spark temperature types representing heat expression state
 */
export type SparkTemperature = "hot" | "ash";

/**
 * Calculate remaining lifetime in milliseconds
 * @param decayAt - ISO timestamp when spark decays (becomes invisible)
 * @returns Remaining time in milliseconds
 */
const calculateRemainingTime = (decayAt: string): number => {
  const now = Date.now();
  const expirationTime = new Date(decayAt).getTime();
  return Math.max(0, expirationTime - now);
};

/**
 * Calculate remaining lifetime in seconds
 * @param decayAt - ISO timestamp when spark decays (becomes invisible)
 * @returns Remaining time in seconds (for countdown timer)
 */
export const calculateRemainingTimeInSeconds = (decayAt: string): number => {
  const remainingMs = calculateRemainingTime(decayAt);
  return Math.floor(remainingMs / 1000);
};

/**
 * Get spark temperature based on remaining lifetime
 *
 * Business Rule (derived from BDD specification):
 * - Hot: Spark has >= 30% of total lifetime remaining (displays as white with ember glow)
 * - Ash: Spark has < 30% of total lifetime remaining (displays as gray, cooling state)
 *
 * The cooling threshold is calculated dynamically based on each spark's total lifetime
 * (decayAt - createdAt), allowing the system to work correctly regardless of the
 * configured decay time setting.
 * @param spark - Spark to evaluate
 * @returns Temperature state ('hot' or 'ash')
 */
export const getSparkTemperature = (spark: Spark): SparkTemperature => {
  const remainingTime = calculateRemainingTime(spark.decayAt);
  const totalLifetime =
    new Date(spark.decayAt).getTime() - new Date(spark.createdAt).getTime();
  const coolingThreshold = totalLifetime * COOLING_THRESHOLD_RATIO;
  return remainingTime >= coolingThreshold ? "hot" : "ash";
};

/**
 * Compute SparkViewModel from Spark domain model
 *
 * Transforms a Spark entity into a view model with computed properties
 * for UI rendering (temperature state and remaining time).
 * @param spark - Spark domain model
 * @returns SparkViewModel with computed temperature and remaining time
 */
export const computeSparkViewModel = (spark: Spark): SparkViewModel => {
  return {
    ...spark,
    temperature: getSparkTemperature(spark),
    remainingTimeInSeconds: calculateRemainingTimeInSeconds(spark.decayAt),
  };
};
