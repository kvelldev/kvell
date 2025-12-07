/**
 * Timeline Page (Smart Component)
 *
 * Entry point for the Timeline feature.
 * Handles dependency injection and wiring of UseCase to UI components.
 */

import { useState } from "react";
import { List } from "lucide-react";
import { wsTimelineRepository } from "@/adapter/repository/wsTimelineRepository";
import { useTimelineStream } from "@/usecase/useTimelineStream";
import { TimelineStream } from "@/components/organisms/TimelineStream";
import { SparkListModal } from "@/components/organisms/SparkListModal";
import { TimelineTemplate } from "@/components/templates/TimelineTemplate";
import { FloatingActionButton } from "@/components/atoms/FloatingActionButton";
import { ErrorStateMessage } from "@/components/molecules/ErrorStateMessage";

/**
 * Timeline Page Component
 *
 * Responsibilities:
 * - Inject wsTimelineRepository into useTimelineStream (DIP)
 * - Pass spark data to TimelineStream organism
 * - Manage "See More" modal state
 * - Display error message if WebSocket connection fails
 * - Wrap content in TimelineTemplate for layout
 * @returns Rendered timeline page
 */
export const TimelinePage = () => {
  // UseCase: Connect to WebSocket and receive sparks
  const { sparks, hasError } = useTimelineStream(wsTimelineRepository);

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <TimelineTemplate>
      {hasError ? (
        <ErrorStateMessage
          title="サーバーに接続できません"
          description="ネットワーク接続を確認してページを再読み込みしてください"
          testId="timeline-error-message"
        />
      ) : (
        <>
          {/* Timeline Stream */}
          <TimelineStream sparks={sparks} />

          {/* See More Button */}
          <FloatingActionButton
            label="もっと見る"
            icon={<List size={20} />}
            onClick={() => {
              setIsModalOpen(true);
            }}
            testId="see-more-button"
          />

          {/* Spark List Modal */}
          <SparkListModal
            sparks={sparks}
            isOpen={isModalOpen}
            onClose={() => {
              setIsModalOpen(false);
            }}
          />
        </>
      )}
    </TimelineTemplate>
  );
};
