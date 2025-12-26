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
}

export const SparkInput = ({
  value,
  onChange,
  maxLength,
  disabled = false,
  testId,
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
    <div className="w-full">
      <Textarea
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
        }}
        placeholder="種火をともす..."
        disabled={disabled}
        data-testid={testId}
        className="caret-ember-500 text-smoke-100 placeholder:text-ash-500 max-h-[40dvh] min-h-[96px] resize-none border-none bg-transparent focus:ring-0 focus:outline-none"
      />
      <div className="mt-2 flex justify-end">
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
