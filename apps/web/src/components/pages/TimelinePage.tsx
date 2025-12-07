/**
 * Timeline Page (Smart Component)
 *
 * Entry point for the Timeline feature.
 * Handles dependency injection and wiring of UseCase to UI components.
 */

import { wsTimelineRepository } from "@/adapter/repository/wsTimelineRepository";
import { useTimelineStream } from "@/usecase/useTimelineStream";
import { TimelineStream } from "@/components/organisms/TimelineStream";
import { TimelineTemplate } from "@/components/templates/TimelineTemplate";
import { ErrorStateMessage } from "@/components/molecules/ErrorStateMessage";

/**
 * Timeline Page Component
 *
 * Responsibilities:
 * - Inject wsTimelineRepository into useTimelineStream (DIP)
 * - Pass spark data to TimelineStream organism
 * - Display error message if WebSocket connection fails
 * - Wrap content in TimelineTemplate for layout
 * @returns Rendered timeline page
 */
export const TimelinePage = () => {
  // UseCase: Connect to WebSocket and receive sparks
  const { sparks, hasError } = useTimelineStream(wsTimelineRepository);

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
    </TimelineTemplate>
  );
};
