/**
 * NewRepliesIndicator Atom
 *
 * A floating indicator that appears when new replies are available
 * while the user is reading past logs (not at bottom of timeline).
 */

import { ArrowDown } from "lucide-react";

interface NewRepliesIndicatorProps {
  /**
   * Whether to show the indicator
   */
  isVisible: boolean;

  /**
   * Callback when the indicator is clicked to scroll to new replies
   */
  onClick: () => void;
}

export const NewRepliesIndicator = ({
  isVisible,
  onClick,
}: NewRepliesIndicatorProps) => {
  if (!isVisible) return null;

  return (
    <button
      onClick={onClick}
      className="rounded-button border-ember-500/30 bg-night-800/80 text-ember-500 hover:border-ember-500/50 hover:bg-night-800 fixed bottom-24 left-1/2 z-40 flex -translate-x-1/2 items-center gap-2 border px-4 py-2 text-sm backdrop-blur-md transition-all"
      data-testid="new-replies-indicator"
      aria-label="新着レスを表示"
    >
      <ArrowDown className="size-4" />
      <span>新着あり</span>
    </button>
  );
};
