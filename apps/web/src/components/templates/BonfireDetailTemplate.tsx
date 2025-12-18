/**
 * BonfireDetailTemplate (Dumb)
 *
 * Layout template for bonfire detail view.
 * Arranges header, timeline, and FAB slots without any business logic.
 */

import { motion, AnimatePresence } from "framer-motion";
import type { ReactNode } from "react";

interface BonfireDetailTemplateProps {
  /**
   * Whether the overlay is open
   */
  isOpen: boolean;

  /**
   * Header slot (BonfireDetailHeader)
   */
  headerSlot: ReactNode;

  /**
   * Timeline slot (ReplyTimeline)
   */
  timelineSlot: ReactNode;

  /**
   * FAB slot (FloatingActionButton)
   */
  fabSlot: ReactNode;

  /**
   * New replies indicator slot
   */
  indicatorSlot?: ReactNode;

  /**
   * Modal slot (SparkPostModal)
   */
  modalSlot?: ReactNode;
}

export const BonfireDetailTemplate = ({
  isOpen,
  headerSlot,
  timelineSlot,
  fabSlot,
  indicatorSlot,
  modalSlot,
}: BonfireDetailTemplateProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="bg-night-900 fixed inset-0 z-50 flex flex-col"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          data-testid="bonfire-detail-overlay"
        >
          {/* Header Area */}
          {headerSlot}

          {/* Response Timeline */}
          <div className="flex-1 overflow-hidden">{timelineSlot}</div>

          {/* New Replies Indicator */}
          {indicatorSlot}

          {/* Floating Action Button */}
          {fabSlot}

          {/* Post Modal */}
          {modalSlot}
        </motion.div>
      )}
    </AnimatePresence>
  );
};
