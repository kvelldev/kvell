/**
 * BonfireDetailPage (Smart Component)
 *
 * Full-screen page for viewing bonfire details and posting replies.
 * Features:
 * - Real-time reply streaming via WebSocket
 * - "Read up to here" marker with LocalStorage persistence
 * - Smart auto-scroll (follows new replies when at bottom)
 * - Share functionality for external SNS
 * - Decay state handling (disables actions when bonfire expires)
 *
 * This is the Smart component that:
 * - Injects dependencies (repositories)
 * - Calls UseCases (hooks)
 * - Passes data and callbacks to Dumb components
 */

import { useState, useCallback, useMemo, useEffect, useRef } from "react";
import { Flame } from "lucide-react";
import type { BonfireViewModel } from "@/domain/model/bonfire";
import type { SparkViewModel } from "@/domain/model/spark";
import { computeSparkViewModel } from "@/domain/service/sparkService";

// Repositories (DIP: inject implementations)
import { wsBonfireRoomRepository } from "@/adapter/repository/wsBonfireRoomRepository";
import { localStorageReadMarkerRepository } from "@/adapter/repository/localStorageReadMarkerRepository";
import { sparkRepository } from "@/adapter/repository/sparkRepository";

// UseCases
import { useBonfireRoom } from "@/usecase/useBonfireRoom";
import { useReadMarker } from "@/usecase/useReadMarker";
import { usePostReply } from "@/usecase/usePostReply";
import { useAddFuel } from "@/usecase/useAddFuel";
import { useConnectionToast } from "@/usecase/useConnectionToast";

// UI Components
import { BonfireDetailTemplate } from "@/components/templates/BonfireDetailTemplate";
import { BonfireDetailHeader } from "@/components/organisms/BonfireDetailHeader";
import { ReplyTimeline } from "@/components/organisms/ReplyTimeline";
import { SparkPostModal } from "@/components/organisms/SparkPostModal";
import { FloatingActionButton } from "@/components/atoms/FloatingActionButton";

// Logger
import { useLogger } from "@/components/useLogger";

/**
 * System-configured character limit for posts
 */
const MAX_CONTENT_LENGTH = 500;

interface BonfireDetailPageProps {
  /**
   * The bonfire to display (null when not open)
   */
  bonfire: BonfireViewModel | null;

  /**
   * Whether the page is open
   */
  isOpen: boolean;

  /**
   * Callback when the page should close
   */
  onClose: () => void;
}

/**
 * Inner component that receives a guaranteed non-null bonfire.
 * This allows hooks to be called unconditionally.
 * @returns Rendered bonfire detail content
 */
const BonfireDetailPageInner = ({
  bonfire,
  isOpen,
  onClose,
}: {
  bonfire: BonfireViewModel;
  isOpen: boolean;
  onClose: () => void;
}) => {
  const logger = useLogger();

  // Local UI state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [postContent, setPostContent] = useState("");

  // UseCases with dependency injection
  const { sparks, isDecayed, addLocalSpark, status } = useBonfireRoom(
    bonfire.id,
    wsBonfireRoomRepository,
  );

  // Connection Toast
  useConnectionToast(status);

  // Ref to track the display marker spark ID for persisted index lookup
  const displayMarkerSparkIdRef = useRef<string | null>(null);

  // Get persisted index for high water mark comparison
  const getPersistedIndex = useCallback(() => {
    if (!displayMarkerSparkIdRef.current) return -1;
    return sparks.findIndex((s) => s.id === displayMarkerSparkIdRef.current);
  }, [sparks]);

  const { displayMarkerSparkId, reportVisiblePosition, commitToStorage } =
    useReadMarker(bonfire.id, localStorageReadMarkerRepository, {
      getPersistedIndex,
    });

  // Keep display marker spark ID in ref for getPersistedIndex
  displayMarkerSparkIdRef.current = displayMarkerSparkId;

  // Commit to storage on unmount (page leave)
  useEffect(() => {
    return () => {
      commitToStorage();
    };
  }, [commitToStorage]);

  // Handler for tracking scroll position (wiring callback to Dumb component)
  const handleVisiblePositionChange = useCallback(
    (sparkId: string, index: number) => {
      reportVisiblePosition(sparkId, index);
    },
    [reportVisiblePosition],
  );

  const {
    postReply,
    isPosting,
    error: postError,
  } = usePostReply(bonfire.id, bonfire.fieldId, sparkRepository, logger);

  const { addFuel } = useAddFuel(sparkRepository, logger);

  // Transform Sparks to ViewModels
  const sparkViewModels: SparkViewModel[] = useMemo(
    () => sparks.map((spark) => computeSparkViewModel(spark)),
    [sparks],
  );

  // Handlers
  const handleOpenModal = useCallback(() => {
    setIsModalOpen(true);
  }, []);

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    setPostContent("");
  }, []);

  const handleSubmitReply = useCallback(async () => {
    if (!postContent.trim()) return;

    const result = await postReply(postContent);
    // Add to local list for optimistic update
    addLocalSpark(result);
    setIsModalOpen(false);
    setPostContent("");
  }, [postContent, postReply, addLocalSpark]);

  const handleAddFuel = useCallback(() => {
    void addFuel({ sparkId: bonfire.sparkId });
  }, [addFuel, bonfire.sparkId]);

  const handleShare = useCallback(() => {
    // Use Web Share API if available, otherwise copy URL to clipboard
    const shareUrl = globalThis.location.href;
    const shareData = {
      title: bonfire.content.slice(0, 50),
      text: bonfire.content,
      url: shareUrl,
    };

    if (typeof navigator.share === "function") {
      void navigator.share(shareData).catch((error: unknown) => {
        // User cancelled or error occurred
        console.info("Share cancelled:", error);
      });
    } else {
      // Fallback: copy URL to clipboard
      void navigator.clipboard
        .writeText(shareUrl)
        .then(() => {
          console.info("URL copied to clipboard");
        })
        .catch((error: unknown) => {
          console.error("Failed to copy URL:", error);
        });
    }
  }, [bonfire.content]);

  return (
    <BonfireDetailTemplate
      isOpen={isOpen}
      headerSlot={
        <BonfireDetailHeader
          bonfire={bonfire}
          isDecayed={isDecayed}
          onClose={onClose}
          onAddFuel={handleAddFuel}
          onShare={handleShare}
        />
      }
      timelineSlot={
        <ReplyTimeline
          sparks={sparkViewModels}
          displayMarkerSparkId={displayMarkerSparkId}
          onVisiblePositionChange={handleVisiblePositionChange}
        />
      }
      fabSlot={
        !isDecayed && (
          <FloatingActionButton
            onClick={handleOpenModal}
            icon={<Flame className="size-6" />}
            label="レスを投稿"
            testId="response-post-fab"
          />
        )
      }
      modalSlot={
        <SparkPostModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          content={postContent}
          onContentChange={setPostContent}
          onSubmit={() => void handleSubmitReply()}
          isPosting={isPosting}
          maxLength={MAX_CONTENT_LENGTH}
          error={postError}
          submitLabel="レスを投げる"
        />
      }
    />
  );
};

export const BonfireDetailPage = ({
  bonfire,
  isOpen,
  onClose,
}: BonfireDetailPageProps) => {
  // Guard: return null if no bonfire (hooks cannot be called conditionally)
  if (!bonfire) {
    return null;
  }

  return (
    <BonfireDetailPageInner
      bonfire={bonfire}
      isOpen={isOpen}
      onClose={onClose}
    />
  );
};
