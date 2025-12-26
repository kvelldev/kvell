/**
 * SparkInput Molecule
 *
 * Textarea with character counter for spark posting.
 * Combines Textarea atom with validation feedback.
 */

import clsx from "clsx";
import { Textarea } from "@/components/ui/textarea";

interface SparkInputProps {
  value: string;
  onChange: (value: string) => void;
  maxLength: number;
  disabled?: boolean;
  testId?: string;
  className?: string;
  autoFocus?: boolean;
}

export const SparkInput = ({
  value,
  onChange,
  maxLength,
  disabled = false,
  testId,
  className,
  autoFocus = false,
}: SparkInputProps) => {
  const currentLength = value.length;
  const isOverLimit = currentLength > maxLength;
  const isNearLimit = currentLength > maxLength * 0.8;

  // Character count color based on limit
  const counterColorClass = isOverLimit
    ? "text-ember-500" // Over limit: ember (warning)
    : isNearLimit
      ? "text-spark-500" // Near limit: spark (attention)
      : "text-ash-500"; // Normal: ash (neutral)

  return (
    <div className="flex w-full flex-col">
      <Textarea
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
        }}
        placeholder="種火をともす..."
        disabled={disabled}
        data-testid={testId}
        autoFocus={autoFocus}
        className={clsx(
          "caret-ember-500 text-smoke-100 placeholder:text-ash-500 min-h-[96px] resize-none border-none bg-transparent focus:ring-0 focus:outline-none",
          className,
        )}
      />
      <div className="mt-2 flex items-center justify-between gap-3">
        <span className="text-ash-500 text-xs font-light">
          薪がないと、時間で消えます
        </span>

        <span
          className={clsx("text-sm font-light", counterColorClass)}
          data-testid={testId ? `${testId}-counter` : undefined}
        >
          {currentLength} / {maxLength}
        </span>
      </div>
    </div>
  );
};
