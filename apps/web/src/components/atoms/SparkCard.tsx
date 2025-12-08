/**
 * SparkCard Atom Component (Dumb)
 *
 * Displays a single spark (種火) with color temperature based heat expression.
 * Pure presentational component with no business logic.
 * Optimized with React.memo to prevent unnecessary re-renders.
 */

import { memo } from "react";
import clsx from "clsx";
import { motion } from "framer-motion";
import type { SparkViewModel } from "@/domain/model/spark";

/**
 * Props for SparkCard component
 */
interface SparkCardProps {
  /**
   * Spark ViewModel with computed temperature state and remaining time
   */
  spark: SparkViewModel;
}

/**
 * Format seconds to mm:ss format for countdown timer display
 * @param totalSeconds - Total remaining seconds
 * @returns Formatted time string (e.g., "09:59", "00:05")
 */
const formatTime = (totalSeconds: number): string => {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
};

/**
 * SparkCard Component (Memoized)
 *
 * Renders a single spark with:
 * - Fade-in animation on mount
 * - Color temperature based heat expression (white→ash transition)
 * - Border glow for hot sparks (ember orange)
 * - TTL countdown timer in bottom-right corner (mm:ss format)
 * - Text truncation for long content
 *
 * Performance:
 * - Memoized to prevent re-renders when temperature state doesn't change
 * - Only re-renders if spark.id, spark.content, spark.temperature, or spark.remainingTimeInSeconds changes
 * @returns Rendered spark card element
 */
const SparkCardComponent = ({ spark }: SparkCardProps) => {
  // Color temperature classes based on pre-computed temperature
  const isHot = spark.temperature === "hot";
  const textColor = isHot ? "text-smoke-100" : "text-ash-500";
  const borderColor = isHot ? "border-ember-500" : "border-transparent";
  const timerColor = isHot ? "text-smoke-400" : "text-ash-600";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={clsx(
        "rounded-card border-2 bg-night-800 p-4 shadow-glow-sm transition-colors duration-1000",
        borderColor,
        textColor,
      )}
      data-testid="spark-item"
    >
      <p className="line-clamp-3 font-base text-sm">{spark.content}</p>
      <div className="mt-2 flex justify-end">
        <span
          className={clsx("font-mono text-xs", timerColor)}
          data-testid="spark-timer"
        >
          {formatTime(spark.remainingTimeInSeconds)}
        </span>
      </div>
    </motion.div>
  );
};

/**
 * Memoized SparkCard
 * Only re-renders when spark data (id, content, temperature) changes
 */
export const SparkCard = memo(SparkCardComponent);
