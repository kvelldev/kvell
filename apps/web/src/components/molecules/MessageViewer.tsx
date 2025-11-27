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
}

export const MessageViewer = ({
  message,
  isLoading,
  error,
}: MessageViewerProps) => {
  if (isLoading) {
    return <div className="text-center text-gray-600">Loading...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800 text-sm font-medium">Error</p>
        <p className="text-red-600 text-sm">{error.message}</p>
      </div>
    );
  }

  if (message) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-md p-4">
        <p className="text-green-800 text-sm font-medium">Success</p>
        <p className="text-green-700 text-sm mt-1">
          <strong>Message:</strong> {message.message}
        </p>
        <p className="text-green-600 text-xs mt-1">ID: {message.id}</p>
        <p className="text-green-600 text-xs">
          Created: {new Date(message.createdAt).toLocaleString()}
        </p>
      </div>
    );
  }

  return null;
};
