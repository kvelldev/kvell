import { memo } from "react";
import clsx from "clsx";
import { motion } from "framer-motion";
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
    <motion.div
      // enterアニメーション
      // initial={{ opacity: 0, y: 20 }}
      // animate={{ opacity: 1, y: 0 }}
      // exitアニメーションを入れるならここ（リストから消える時）

      // transition-all にして shadow の消失もふわっとさせる
      // duration-1000 により、"やがて冷めていく" 情緒的な変化を表現
      className={clsx(
        "rounded-card border bg-night-800 p-4 text-ash-500 transition-all duration-1000 ease-in-out",
        shadowClass,
        borderClass,
      )}
      data-testid="spark-item"
      data-temperature={spark.temperature} // テスト用に状態をDOMに出しておく
    >
      <p className="line-clamp-3 font-base text-sm leading-relaxed">
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
    </motion.div>
  );
};

export const SparkCard = memo(SparkCardComponent);
