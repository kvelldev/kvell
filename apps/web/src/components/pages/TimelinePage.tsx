/**
 * Timeline Page (Smart Component)
 *
 * Entry point for the Timeline feature.
 * Handles dependency injection and wiring of UseCase to UI components.
 * Includes spark posting functionality with FAB and modal.
 */

import { useState } from "react";
import { Flame } from "lucide-react";
import { wsTimelineRepository } from "@/adapter/repository/wsTimelineRepository";
import { sparkRepository } from "@/adapter/repository/sparkRepository";
import { useTimelineStream } from "@/usecase/useTimelineStream";
import { usePostSpark } from "@/usecase/usePostSpark";
import { TimelineStream } from "@/components/organisms/TimelineStream";
import { TimelineTemplate } from "@/components/templates/TimelineTemplate";
import { ErrorStateMessage } from "@/components/molecules/ErrorStateMessage";
import { FloatingActionButton } from "@/components/atoms/FloatingActionButton";
import { SparkPostModal } from "@/components/organisms/SparkPostModal";
import { useLogger } from "@/components/useLogger";
import { settings } from "@/adapter/infra/settings";

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
  // Local UI state for posting
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [content, setContent] = useState("");

  // Dependency Injection: Logger
  const logger = useLogger();

  // UseCase: Connect to WebSocket and receive sparks
  const { sparks, hasError } = useTimelineStream(wsTimelineRepository);

  // UseCase: Post spark
  const { postSpark, isPosting, error } = usePostSpark(sparkRepository, logger);

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

  return (
    <TimelineTemplate>
      {hasError ? (
        <ErrorStateMessage
          title="サーバーに接続できません"
          description="ネットワーク接続を確認してページを再読み込みしてください"
          testId="timeline-error-message"
        />
      ) : (
        <TimelineStream sparks={sparks} />
      )}

      <FloatingActionButton
        onClick={() => {
          setIsModalOpen(true);
        }}
        icon={<Flame size={24} />}
        label="種火を投げる"
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
    </TimelineTemplate>
  );
};
