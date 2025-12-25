/**
 * Timeline Page (Smart Component)
 *
 * Entry point for the Timeline feature.
 * Handles dependency injection and wiring of UseCase to UI components.
 * Includes spark posting functionality with FAB and modal.
 */

import { useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Flame } from "lucide-react";
import { LayoutGroup } from "framer-motion";
import { wsTimelineRepository } from "@/adapter/repository/wsTimelineRepository";
import { bonfireRepository } from "@/adapter/repository/bonfireRepository";
import { sparkRepository } from "@/adapter/repository/sparkRepository";
import { triggerHapticFeedback } from "@/adapter/infra/haptic";
import { useTimelineStream } from "@/usecase/useTimelineStream";
import { usePostSpark } from "@/usecase/usePostSpark";
import { useAddFuel } from "@/usecase/useAddFuel";
import { useBonfire } from "@/usecase/useBonfire";
import { useConnectionToast } from "@/usecase/useConnectionToast";
import { TimelineStream } from "@/components/organisms/TimelineStream";
import { TimelineTemplate } from "@/components/templates/TimelineTemplate";
import { ErrorStateMessage } from "@/components/molecules/ErrorStateMessage";
import { FloatingActionButton } from "@/components/atoms/FloatingActionButton";
import { SparkPostModal } from "@/components/organisms/SparkPostModal";
import { BonfireCarousel } from "@/components/organisms/BonfireCarousel";
import { BonfireDetailPage } from "@/components/pages/BonfireDetailPage";
import { useLogger } from "@/components/useLogger";
import { settings } from "@/adapter/infra/settings";
import { LOG_EVENTS } from "@/domain/constants";
import type { BonfireViewModel } from "@/domain/model/bonfire";

/**
 * Timeline Page Component
 *
 * Responsibilities:
 * - Display real-time timeline of sparks
 * - Provide FAB button to open spark posting modal
 * - Handle spark posting with error display
 * @returns Rendered timeline page with posting capability
 */
export const TimelinePage = () => {
  // Routing: Get bonfireId from URL params for deep linking support
  const { bonfireId } = useParams<{ bonfireId: string }>();
  const navigate = useNavigate();

  // Local UI state for posting
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [content, setContent] = useState("");

  // Dependency Injection: Logger
  const logger = useLogger();

  // UseCase: Fetch bonfires
  const { bonfires, refetch: refetchBonfires } = useBonfire(bonfireRepository);

  // UseCase: Connect to WebSocket and receive sparks
  const { sparks, status } = useTimelineStream({
    repository: wsTimelineRepository,
    onBonfirePromoted: () => {
      // Refresh bonfire list when a spark receives promotion event
      void refetchBonfires();
    },
  });

  // UI: Handle connection status with Toast (Custom Hook)
  useConnectionToast(status);

  // UseCase: Post spark
  const { postSpark, isPosting, error } = usePostSpark(sparkRepository, logger);

  // UseCase: Add fuel to spark
  const { addFuel } = useAddFuel(sparkRepository, logger);

  // Derive selected bonfire from URL params (for deep linking & browser back support)
  const selectedBonfire = useMemo(() => {
    if (!bonfireId) return null;
    return bonfires.find((b) => b.id === bonfireId) ?? null;
  }, [bonfireId, bonfires]);

  // Event Handler: Submit spark
  const handleSubmit = async () => {
    const trimmedContent = content.trim();
    if (!trimmedContent) return;

    try {
      await postSpark({ content: trimmedContent });
      // On success: Clear input and close modal
      setContent("");
      setIsModalOpen(false);
    } catch {
      // Error is already logged by UseCase and stored in error state
      // UI will display error via SparkPostModal
    }
  };

  // Event Handler: Add fuel to spark
  const handleAddFuel = (sparkId: string) => {
    // Trigger haptic feedback (UI layer responsibility)
    const hapticTriggered = triggerHapticFeedback();
    if (!hapticTriggered) {
      logger.info("Haptic feedback not supported", {
        event: LOG_EVENTS.ADD_FUEL.HAPTIC_NOT_SUPPORTED,
      });
    }

    // Execute UseCase
    void addFuel({ sparkId });
  };

  // Event Handler: Open bonfire detail overlay (navigate to bonfire detail URL)
  const handleBonfireClick = (bonfire: BonfireViewModel) => {
    void navigate(`/timeline/bonfire/${bonfire.id}`);
  };

  // Event Handler: Close bonfire detail overlay (navigate back)
  const handleBonfireClose = () => {
    void navigate("/timeline");
  };

  return (
    <LayoutGroup>
      <TimelineTemplate
        bonfireArea={
          <BonfireCarousel
            bonfires={bonfires}
            onBonfireClick={handleBonfireClick}
          />
        }
        sparkArea={
          // Show ErrorStateMessage ONLY if there are no sparks (initial load failure)
          status.type === "error" && sparks.length === 0 ? (
            <ErrorStateMessage
              title="サーバーに接続できません"
              description="ネットワーク接続を確認してページを再読み込みしてください"
              testId="timeline-error-message"
            />
          ) : (
            <TimelineStream sparks={sparks} onAddFuel={handleAddFuel} />
          )
        }
      />

      <FloatingActionButton
        onClick={() => {
          setIsModalOpen(true);
        }}
        icon={<Flame size={24} />}
        label="種火をともす"
        testId="spark-post-fab"
      />

      <SparkPostModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
        }}
        content={content}
        onContentChange={setContent}
        onSubmit={() => {
          void handleSubmit();
        }}
        isPosting={isPosting}
        maxLength={settings.sparkMaxLength}
        error={error}
      />

      <BonfireDetailPage
        bonfire={selectedBonfire}
        isOpen={selectedBonfire !== null}
        onClose={handleBonfireClose}
      />
    </LayoutGroup>
  );
};
