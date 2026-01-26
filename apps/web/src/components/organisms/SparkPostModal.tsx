/**
 * SparkPostModal Organism
 *
 * Modal dialog for posting sparks.
 * Contains SparkInput, error display, and submit button directly.
 */

import { useState, useEffect } from "react";
import { X } from "lucide-react";
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
   * @default "種火をともす"
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
  submitLabel = "種火をともす",
}: SparkPostModalProps) => {
  const trimmedContent = content.trim();
  const isEmpty = trimmedContent.length === 0;
  const isOverLimit = content.length > maxLength;
  const isSubmitDisabled = isEmpty || isOverLimit || isPosting;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogOverlay />
      <DialogContent className="bg-background/80 data-[state=closed]:slide-out-to-left-0 data-[state=closed]:slide-out-to-top-0 data-[state=open]:slide-in-from-left-0 data-[state=open]:slide-in-from-top-0 sm:bg-background sm:data-[state=closed]:slide-out-to-left-1/2 sm:data-[state=closed]:slide-out-to-top-[48%] sm:data-[state=open]:slide-in-from-left-1/2 sm:data-[state=open]:slide-in-from-top-[48%] fixed top-0 right-0 bottom-0 left-0 z-50 flex h-[100dvh] w-screen max-w-none translate-x-0 translate-y-0 flex-col rounded-none border-0 p-0 backdrop-blur-xl transition-all duration-200 sm:top-[50%] sm:left-[50%] sm:h-auto sm:max-h-none sm:max-w-2xl sm:translate-x-[-50%] sm:translate-y-[-50%] sm:rounded-lg sm:border sm:p-6 sm:backdrop-blur-none [&>button.absolute]:hidden sm:[&>button.absolute]:flex">
        {/* Visually hidden title for screen reader accessibility */}
        <DialogTitle className="sr-only">{submitLabel}</DialogTitle>

        {/* Mobile Header */}
        <div className="flex items-center justify-between border-b border-white/10 px-4 py-3 sm:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="text-white/70 hover:bg-white/10"
          >
            <X className="h-6 w-6" />
          </Button>
          <Button onClick={onSubmit} disabled={isSubmitDisabled} size="sm">
            {isPosting ? "投稿中..." : submitLabel}
          </Button>
        </div>

        <div className="flex min-h-0 flex-1 flex-col p-4 sm:p-0">
          <SparkInput
            value={content}
            onChange={onContentChange}
            maxLength={maxLength}
            disabled={isPosting}
            testId="spark-input"
            className="h-full flex-1 sm:h-auto sm:flex-none"
            autoFocus={true}
          />
        </div>

        {error && (
          <div
            className="rounded-card border-ember-500/20 bg-ember-500/5 mt-3 flex-none border p-3 backdrop-blur-sm sm:mt-4"
            data-testid="spark-error"
          >
            <p className="text-ember-500 text-sm font-light">
              エラー: {error.message}
            </p>
          </div>
        )}

        {/* Desktop Footer */}
        <div className="mt-4 hidden justify-end sm:flex">
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
