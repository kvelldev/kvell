/**
 * SparkCard Atom Component (Dumb)
 *
 * Displays a single spark (種火) with color temperature based heat expression.
 * Pure presentational component with no business logic.
 */

import { motion } from "framer-motion";
import type { Spark } from "@/domain/model/spark";

/**
 * Props for SparkCard component
 */
interface SparkCardProps {
  /**
   * Spark data to display
   */
  spark: Spark;
}

/**
 * Cooling threshold in milliseconds (3 minutes)
 * Sparks with less than 3 minutes remaining will display as "cooling"
 */
const COOLING_THRESHOLD_MS = 3 * 60 * 1000;

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
 * SparkCard Component
 *
 * Renders a single spark with:
 * - Fade-in animation on mount (opacity only, no persistent opacity reduction)
 * - Color temperature based heat expression (white→ash transition)
 * - Border glow for hot sparks (ember orange)
 * - Text truncation for long content
 * @returns Rendered spark card element
 */
export const SparkCard = ({ spark }: SparkCardProps) => {
  const remainingTime = calculateRemainingTime(spark.visibleUntil);
  const isHot = remainingTime >= COOLING_THRESHOLD_MS;

  // Color temperature classes
  const textColor = isHot ? "text-smoke-100" : "text-ash-500";
  const borderColor = isHot ? "border-ember-500" : "border-transparent";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className={`rounded-card border-2 bg-night-800 p-4 shadow-glow-sm ${borderColor} ${textColor} transition-colors duration-1000`}
      data-testid={`spark-card-${spark.id}`}
    >
      <p className="line-clamp-3 font-base text-sm">{spark.content}</p>
    </motion.div>
  );
};
