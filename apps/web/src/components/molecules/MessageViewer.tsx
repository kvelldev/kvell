/**
 * Message Viewer Molecule
 *
 * Displays health check message or status (Dumb Component).
 */

import type { HealthMessage } from "@/domain/model/health";

interface MessageViewerProps {
  message: HealthMessage | null;
  isLoading: boolean;
  error: Error | null | undefined;
  formattedCreatedAt?: string;
}

export const MessageViewer = ({
  message,
  isLoading,
  error,
  formattedCreatedAt,
}: MessageViewerProps) => {
  if (isLoading) {
    return (
      <div
        className="text-center font-light text-ash-500"
        data-testid="health-loading-display"
      >
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="rounded-card border border-ash-500 bg-night-800 p-4"
        data-testid="health-error-display"
      >
        <p className="text-sm font-light text-ash-500">Error</p>
        <p className="mt-1 text-sm text-smoke-100">{error.message}</p>
      </div>
    );
  }

  if (message) {
    return (
      <div
        className="rounded-card border border-ember-500 bg-night-800 p-4 shadow-glow-sm"
        data-testid="health-message-display"
      >
        <p className="text-sm font-light text-ember-500">Success</p>
        <p className="mt-1 text-sm text-smoke-100">
          <strong className="text-ember-500">Message:</strong> {message.message}
        </p>
        <p className="mt-1 text-xs text-ash-500">ID: {message.id}</p>
        <p className="text-xs text-ash-500">
          Created: {formattedCreatedAt ?? message.createdAt}
        </p>
      </div>
    );
  }

  return null;
};
