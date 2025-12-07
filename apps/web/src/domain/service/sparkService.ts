/**
 * Spark Domain Service
 *
 * Pure business logic for spark-related calculations.
 * No dependencies on UI or infrastructure.
 */

import type { Spark } from "@/domain/model/spark";
import { COOLING_THRESHOLD_MS } from "@/domain/constants";

/**
 * Spark temperature types representing heat expression state
 */
export type SparkTemperature = "hot" | "ash";

/**
 * Calculate remaining lifetime in milliseconds
 * @param visibleUntil - ISO timestamp when spark expires
 * @returns Remaining time in milliseconds
 */
const calculateRemainingTime = (visibleUntil: string): number => {
  const now = Date.now();
  const expirationTime = new Date(visibleUntil).getTime();
  return Math.max(0, expirationTime - now);
};

/**
 * Calculate remaining lifetime in seconds
 * @param visibleUntil - ISO timestamp when spark expires
 * @returns Remaining time in seconds (for countdown timer)
 */
export const calculateRemainingTimeInSeconds = (
  visibleUntil: string,
): number => {
  const remainingMs = calculateRemainingTime(visibleUntil);
  return Math.floor(remainingMs / 1000);
};

/**
 * Get spark temperature based on remaining lifetime
 *
 * Business Rule:
 * - Hot: Spark has >= 3 minutes remaining (displays as white with ember border)
 * - Ash: Spark has < 3 minutes remaining (displays as gray, cooling state)
 * @param spark - Spark to evaluate
 * @returns Temperature state ('hot' or 'ash')
 */
export const getSparkTemperature = (spark: Spark): SparkTemperature => {
  const remainingTime = calculateRemainingTime(spark.visibleUntil);
  return remainingTime >= COOLING_THRESHOLD_MS ? "hot" : "ash";
};
