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
}: SparkPostModalProps) => {
  const trimmedContent = content.trim();
  const isEmpty = trimmedContent.length === 0;
  const isOverLimit = content.length > maxLength;
  const isSubmitDisabled = isEmpty || isOverLimit || isPosting;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogOverlay />
      <DialogContent className="max-w-2xl">
        <SparkInput
          value={content}
          onChange={onContentChange}
          maxLength={maxLength}
          disabled={isPosting}
          testId="spark-input"
        />

        {error && (
          <div
            className="mt-3 rounded-card border border-ember-500/20 bg-ember-500/5 p-3 backdrop-blur-sm"
            data-testid="spark-error"
          >
            <p className="text-sm font-light text-ember-500">
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
            {isPosting ? "投稿中..." : "種火を投げる"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
