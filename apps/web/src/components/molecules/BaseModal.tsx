/**
 * BaseModal Molecule Component (Dumb)
 *
 * Generic modal component providing:
 * - Backdrop with click-to-close
 * - Modal container with animations
 * - Header with title and close button
 * - Scrollable content area
 */

import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import type { ReactNode } from "react";

/**
 * Props for BaseModal component
 */
interface BaseModalProps {
  /**
   * Whether the modal is open
   */
  isOpen: boolean;

  /**
   * Callback to close the modal
   */
  onClose: () => void;

  /**
   * Modal title displayed in header
   */
  title: string;

  /**
   * Modal content
   */
  children: ReactNode;

  /**
   * Optional test ID for backdrop
   */
  backdropTestId?: string;

  /**
   * Optional test ID for modal content
   */
  modalTestId?: string;

  /**
   * Optional test ID for close button
   */
  closeButtonTestId?: string;
}

/**
 * BaseModal Component
 *
 * Features:
 * - Full-screen backdrop overlay (90% opacity)
 * - Centered modal with max-width and max-height constraints
 * - Fade + scale animation on open/close
 * - Click backdrop or close button to dismiss
 * - Scrollable content area
 * @returns Rendered modal element
 */
export const BaseModal = ({
  isOpen,
  onClose,
  title,
  children,
  backdropTestId,
  modalTestId,
  closeButtonTestId,
}: BaseModalProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.9 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 bg-night-900"
            onClick={onClose}
            data-testid={backdropTestId}
          />

          {/* Modal Content */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            data-testid={modalTestId}
          >
            <div className="flex max-h-[80vh] w-full max-w-2xl flex-col rounded-card bg-night-800 shadow-glow-md">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-ash-500 p-6">
                <h2 className="font-base text-xl font-normal text-smoke-100">
                  {title}
                </h2>
                <button
                  onClick={onClose}
                  className="text-ash-500 transition-colors hover:text-smoke-100"
                  data-testid={closeButtonTestId}
                >
                  <X size={24} />
                </button>
              </div>

              {/* Content Area (Scrollable) */}
              <div className="flex-1 overflow-y-auto p-6">{children}</div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
