import { memo } from "react";
import clsx from "clsx";
import type { SparkViewModel } from "@/domain/model/spark";

interface SparkCardProps {
  spark: SparkViewModel;
}

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
 * - Dynamic glow: Visible when hot, disappears when cooled (Ash)
 * - TTL countdown timer in bottom-right corner
 * - Text truncation for long content
 *
 * Performance:
 * - Memoized to prevent re-renders when temperature state doesn't change
 * - Only re-renders if spark.id, spark.content, spark.temperature, or spark.remainingTimeInSeconds changes
 * @returns Rendered spark card element
 */
const SparkCardComponent = ({ spark }: SparkCardProps) => {
  const isHot = spark.temperature === "hot";

  const shadowClass = isHot ? "shadow-glow-sm" : "shadow-none";
  const borderClass = isHot ? "border-ember-500" : "border-ash-500";

  return (
    <div
      className={clsx(
        "rounded-card bg-night-800 text-ash-500 border p-4 transition-all duration-1000 ease-in-out",
        shadowClass,
        borderClass,
      )}
      data-testid="spark-item"
      data-temperature={spark.temperature} // テスト用に状態をDOMに出しておく
    >
      <p className="font-base line-clamp-3 text-sm leading-relaxed">
        {spark.content}
      </p>
      <div className="mt-2 flex justify-end">
        <span
          className={clsx("font-mono text-xs transition-colors duration-1000")}
          data-testid="spark-timer"
        >
          {formatTime(spark.remainingTimeInSeconds)}
        </span>
      </div>
    </div>
  );
};

export const SparkCard = memo(SparkCardComponent);
