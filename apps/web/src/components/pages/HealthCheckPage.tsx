/**
 * Health Check Page
 *
 * Page component for E2E health check (Smart Component).
 * Only handles logic wiring - no DOM structure or styling.
 */

import { useState } from "react";
import {
  useFetchLatestHealthMessage,
  useSaveHealthMessage,
} from "@/usecase/useHealthCheck";
import { healthRepository } from "@/adapter/repository/healthRepository";
import { HealthCheckTemplate } from "@/components/templates/HealthCheckTemplate";
import { HealthCheckMonitor } from "@/components/organisms/HealthCheckMonitor";
import { useLogger } from "@/components/useLogger";

export const HealthCheckPage = () => {
  const [inputText, setInputText] = useState("");

  // Get logger from context (Page is responsible for DI)
  const logger = useLogger();

  // Inject repository and logger dependencies into UseCases
  const {
    message,
    isLoading: isFetching,
    error: fetchError,
    refetch,
  } = useFetchLatestHealthMessage(healthRepository, logger);
  const {
    saveMessage,
    isSaving,
    error: saveError,
  } = useSaveHealthMessage(healthRepository, logger);

  // Event handlers (logic wiring)
  const handleSave = () => {
    if (!inputText.trim()) return;
    void saveMessage(inputText);
    setInputText("");
  };

  const handleFetchLatest = () => {
    void refetch();
  };

  // Aggregate states
  const isLoading = isFetching || isSaving;
  const error = saveError ?? fetchError;

  // Render: delegate to Template and Organism
  return (
    <HealthCheckTemplate>
      <HealthCheckMonitor
        inputValue={inputText}
        onInputChange={setInputText}
        onSave={handleSave}
        onFetch={handleFetchLatest}
        message={message}
        isLoading={isLoading}
        error={error}
      />
    </HealthCheckTemplate>
  );
};
