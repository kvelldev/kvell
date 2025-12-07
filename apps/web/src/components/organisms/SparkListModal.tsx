/**
 * SparkListModal Organism Component (Dumb)
 *
 * Modal displaying all currently alive sparks.
 * Used for "See More" feature to view sparks that have scrolled off-screen.
 *
 * Responsibilities:
 * - Render list of sparks using SparkCard
 * - Display empty state message when no sparks available
 * - Compose BaseModal for modal structure
 */

import type { Spark } from "@/domain/model/spark";
import { BaseModal } from "@/components/molecules/BaseModal";
import { SparkCard } from "@/components/atoms/SparkCard";

/**
 * Props for SparkListModal component
 */
interface SparkListModalProps {
  /**
   * Array of sparks to display
   */
  sparks: Spark[];

  /**
   * Whether the modal is open
   */
  isOpen: boolean;

  /**
   * Callback to close the modal
   */
  onClose: () => void;
}

/**
 * SparkListModal Component
 *
 * Features:
 * - Scrollable list of all alive sparks
 * - Color temperature expression (same as timeline)
 * - Empty state handling
 * @returns Rendered modal element
 */
export const SparkListModal = ({
  sparks,
  isOpen,
  onClose,
}: SparkListModalProps) => {
  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      title={`全ての種火 (${String(sparks.length)})`}
      backdropTestId="spark-list-backdrop"
      modalTestId="spark-list-modal"
      closeButtonTestId="close-modal-button"
    >
      {/* Spark List */}
      <div className="space-y-4">
        {sparks.length === 0 ? (
          <p className="py-8 text-center text-ash-500">
            表示できる種火がありません
          </p>
        ) : (
          sparks.map((spark) => <SparkCard key={spark.id} spark={spark} />)
        )}
      </div>
    </BaseModal>
  );
};
