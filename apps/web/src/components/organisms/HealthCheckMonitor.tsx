/**
 * Health Check Monitor Organism
 *
 * Combines ActionForm and MessageViewer (Dumb Component).
 * Displays the complete health check interface.
 */

import type { HealthMessage } from "@/domain/model/health";
import { ActionForm } from "@/components/molecules/ActionForm";
import { MessageViewer } from "@/components/molecules/MessageViewer";

interface HealthCheckMonitorProps {
  inputValue: string;
  onInputChange: (value: string) => void;
  onSave: () => void;
  onFetch: () => void;
  message: HealthMessage | null;
  isLoading: boolean;
  error: Error | null | undefined;
}

export const HealthCheckMonitor = ({
  inputValue,
  onInputChange,
  onSave,
  onFetch,
  message,
  isLoading,
  error,
}: HealthCheckMonitorProps) => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-light text-smoke-100 text-center">
        System Health Check
      </h1>

      <ActionForm
        inputValue={inputValue}
        onInputChange={onInputChange}
        onSave={onSave}
        onFetch={onFetch}
        isLoading={isLoading}
      />

      <MessageViewer message={message} isLoading={isLoading} error={error} />
    </div>
  );
};
