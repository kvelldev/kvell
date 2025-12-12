import { memo, useState, useCallback } from "react";
import clsx from "clsx";
import { Flame } from "lucide-react";
import type { SparkViewModel } from "@/domain/model/spark";
import { IgniteEffect } from "@/components/atoms/IgniteEffect";

interface SparkCardProps {
  spark: SparkViewModel;
  /**
   * Callback when fuel button is clicked
   */
  onAddFuel?: (sparkId: string) => void;
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
 * - Add fuel button with ignite effect
 *
 * Performance:
 * - Memoized to prevent re-renders when temperature state doesn't change
 * - Only re-renders if spark.id, spark.content, spark.temperature, or spark.remainingTimeInSeconds changes
 * @returns Rendered spark card element
 */
const SparkCardComponent = ({ spark, onAddFuel }: SparkCardProps) => {
  const isHot = spark.temperature === "hot";
  const [showEffect, setShowEffect] = useState(false);

  const shadowClass = isHot ? "shadow-glow-sm" : "shadow-none";
  // Glassmorphism: soft borders with glow (not hard lines)
  const borderClass = isHot
    ? "border border-ember-500/50 ring-1 ring-ember-500/20"
    : "border border-white/10";

  const handleAddFuel = () => {
    // Trigger ignite effect
    setShowEffect(true);
    // Call parent callback
    onAddFuel?.(spark.id);
  };

  // Memoize onComplete to prevent IgniteEffect useEffect from re-firing on every render
  const handleEffectComplete = useCallback(() => {
    setShowEffect(false);
  }, []);

  return (
    <div
      className={clsx(
        // Glassmorphism: translucent background with backdrop blur
        "rounded-card bg-night-800/40 backdrop-blur-md text-ash-500 p-4 transition-all duration-1000 ease-in-out",
        shadowClass,
        borderClass,
      )}
      data-testid="spark-item"
      data-temperature={spark.temperature} // テスト用に状態をDOMに出しておく
    >
      <p className="font-base line-clamp-3 text-sm leading-relaxed">
        {spark.content}
      </p>
      <div className="mt-2 flex items-center justify-between">
        {/* Add Fuel Button */}
        <button
          onClick={handleAddFuel}
          className={clsx(
            "relative flex items-center gap-1.5 rounded-button px-3 py-1.5 text-xs font-medium transition-all",
            "border border-ember-500/30 bg-ember-500/10 text-ember-500",
            "hover:border-ember-500/50 hover:bg-ember-500/20",
            "focus:outline-none focus:ring-2 focus:ring-ember-500/50",
          )}
          data-testid="add-fuel-button"
          aria-label="Add fuel to spark"
        >
          <Flame className="h-3.5 w-3.5" />
          <span>薪をくべる</span>
          <IgniteEffect trigger={showEffect} onComplete={handleEffectComplete} />
        </button>

        {/* TTL Timer */}
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
