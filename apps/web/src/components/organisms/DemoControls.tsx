/**
 * DemoControls Component
 *
 * Admin buttons for seeding and cleaning up demo bonfires.
 */

import { useState } from "react";
import { debugRepository } from "@/adapter/repository/debugRepository";

export const DemoControls = ({ onSuccess }: { onSuccess?: () => void }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const handleSeed = async () => {
    setIsLoading(true);
    setMessage(null);
    try {
      const result = await debugRepository.seedBonfires();
      setMessage(result);
      onSuccess?.();
    } catch (error) {
      setMessage("Seed failed");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCleanup = async () => {
    setIsLoading(true);
    setMessage(null);
    try {
      const result = await debugRepository.cleanupBonfires();
      setMessage(result);
      onSuccess?.();
    } catch (error) {
      setMessage("Cleanup failed");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-start gap-2">
      {message && (
        <div className="rounded-md bg-gray-800/90 px-3 py-1 text-sm text-white">
          {message}
        </div>
      )}
      <div className="flex gap-2">
        <button
          onClick={handleSeed}
          disabled={isLoading}
          className="rounded-full bg-orange-500 px-4 py-2 text-sm font-medium text-white shadow-lg transition hover:bg-orange-600 disabled:opacity-50"
        >
          Seed
        </button>
        <button
          onClick={handleCleanup}
          disabled={isLoading}
          className="rounded-full bg-gray-600 px-4 py-2 text-sm font-medium text-white shadow-lg transition hover:bg-gray-700 disabled:opacity-50"
        >
          Cleanup
        </button>
      </div>
    </div>
  );
};
