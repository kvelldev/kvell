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
        className="text-center text-ash-500 font-light"
        data-testid="health-loading-display"
      >
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="bg-night-800 border border-ash-500 rounded-card p-4"
        data-testid="health-error-display"
      >
        <p className="text-ash-500 text-sm font-light">Error</p>
        <p className="text-smoke-100 text-sm mt-1">{error.message}</p>
      </div>
    );
  }

  if (message) {
    return (
      <div
        className="bg-night-800 border border-ember-500 rounded-card shadow-glow-sm p-4"
        data-testid="health-message-display"
      >
        <p className="text-ember-500 text-sm font-light">Success</p>
        <p className="text-smoke-100 text-sm mt-1">
          <strong className="text-ember-500">Message:</strong> {message.message}
        </p>
        <p className="text-ash-500 text-xs mt-1">ID: {message.id}</p>
        <p className="text-ash-500 text-xs">
          Created: {formattedCreatedAt ?? message.createdAt}
        </p>
      </div>
    );
  }

  return null;
};
