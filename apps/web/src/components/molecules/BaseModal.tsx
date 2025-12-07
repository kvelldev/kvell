/**
 * BaseModal Molecule Component (Dumb)
 *
 * Generic modal component providing:
 * - Backdrop with click-to-close
 * - Modal container with animations
 * - Header with title and close button
 * - Scrollable content area
 *
 * Built with Headless UI Dialog for accessibility features:
 * - Automatic focus management
 * - Keyboard navigation (ESC to close)
 * - ARIA attributes
 * - Focus trap
 */

import { Dialog, DialogPanel, DialogTitle } from "@headlessui/react";
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
 * - Click backdrop or ESC key to dismiss
 * - Scrollable content area
 * - Accessibility features via Headless UI Dialog
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
        <Dialog
          static
          open={isOpen}
          onClose={onClose}
          className="relative z-50"
        >
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.9 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-night-900"
            data-testid={backdropTestId}
          />

          {/* Modal Container */}
          <div className="fixed inset-0 flex items-center justify-center p-4">
            <DialogPanel>
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.2 }}
                className="flex max-h-[80vh] w-full max-w-2xl flex-col rounded-card bg-night-800 shadow-glow-md"
                data-testid={modalTestId}
              >
                {/* Header */}
                <div className="flex items-center justify-between border-b border-ash-500 p-6">
                  <DialogTitle className="font-base text-xl font-normal text-smoke-100">
                    {title}
                  </DialogTitle>
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
              </motion.div>
            </DialogPanel>
          </div>
        </Dialog>
      )}
    </AnimatePresence>
  );
};
