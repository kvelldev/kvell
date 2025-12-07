/**
 * SparkPostForm Organism
 *
 * Complete spark posting form with input, validation, and submit button.
 * Dumb component - receives all data and handlers via props.
 */

import { SparkInput } from "@/components/molecules/SparkInput";
import { Button } from "@/components/atoms/Button";

interface SparkPostFormProps {
  content: string;
  onContentChange: (value: string) => void;
  onSubmit: () => void;
  isPosting: boolean;
  maxLength: number;
  error?: Error | null;
}

export const SparkPostForm = ({
  content,
  onContentChange,
  onSubmit,
  isPosting,
  maxLength,
  error,
}: SparkPostFormProps) => {
  const trimmedContent = content.trim();
  const isEmpty = trimmedContent.length === 0;
  const isOverLimit = content.length > maxLength;
  const isSubmitDisabled = isEmpty || isOverLimit || isPosting;

  return (
    <div className="mx-auto w-full max-w-2xl rounded-card bg-night-800 p-6 shadow-glow-sm">
      <h2 className="mb-4 text-xl font-light text-ember-500">種火を投げる</h2>

      <SparkInput
        value={content}
        onChange={onContentChange}
        maxLength={maxLength}
        disabled={isPosting}
        testId="spark-input"
      />

      {error && (
        <div
          className="mt-3 text-sm font-light text-ember-500"
          data-testid="spark-error"
        >
          エラー: {error.message}
        </div>
      )}

      <div className="mt-4 flex justify-end">
        <Button
          onClick={onSubmit}
          disabled={isSubmitDisabled}
          testId="spark-submit-button"
        >
          {isPosting ? "投稿中..." : "種火を投げる"}
        </Button>
      </div>
    </div>
  );
};
