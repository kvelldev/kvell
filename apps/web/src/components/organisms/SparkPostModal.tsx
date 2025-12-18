/**
 * SparkPostModal Organism
 *
 * Modal dialog for posting sparks.
 * Contains SparkInput, error display, and submit button directly.
 */

import {
  Dialog,
  DialogContent,
  DialogOverlay,
  DialogTitle,
} from "@/components/ui/dialog";
import { SparkInput } from "@/components/molecules/SparkInput";
import { Button } from "@/components/ui/button";

interface SparkPostModalProps {
  isOpen: boolean;
  onClose: () => void;
  content: string;
  onContentChange: (value: string) => void;
  onSubmit: () => void;
  isPosting: boolean;
  maxLength: number;
  error?: Error | null;
  /**
   * Custom label for the submit button
   * @default "種火を投げる"
   */
  submitLabel?: string;
}

export const SparkPostModal = ({
  isOpen,
  onClose,
  content,
  onContentChange,
  onSubmit,
  isPosting,
  maxLength,
  error,
  submitLabel = "種火を投げる",
}: SparkPostModalProps) => {
  const trimmedContent = content.trim();
  const isEmpty = trimmedContent.length === 0;
  const isOverLimit = content.length > maxLength;
  const isSubmitDisabled = isEmpty || isOverLimit || isPosting;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogOverlay />
      <DialogContent className="max-w-2xl">
        {/* Visually hidden title for screen reader accessibility */}
        <DialogTitle className="sr-only">{submitLabel}</DialogTitle>
        <SparkInput
          value={content}
          onChange={onContentChange}
          maxLength={maxLength}
          disabled={isPosting}
          testId="spark-input"
        />

        {error && (
          <div
            className="rounded-card border-ember-500/20 bg-ember-500/5 mt-3 border p-3 backdrop-blur-sm"
            data-testid="spark-error"
          >
            <p className="text-ember-500 text-sm font-light">
              エラー: {error.message}
            </p>
          </div>
        )}

        <div className="mt-4 flex justify-end">
          <Button
            onClick={onSubmit}
            disabled={isSubmitDisabled}
            data-testid="spark-submit-button"
          >
            {isPosting ? "投稿中..." : submitLabel}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
