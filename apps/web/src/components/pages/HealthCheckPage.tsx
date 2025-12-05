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
import { LOG_EVENTS } from "@/domain/constants";

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

    // Execute async operation without blocking
    void saveMessage(inputText)
      .then(() => {
        setInputText("");
      })
      .catch((error: unknown) => {
        // SWRの状態(error)でUIは制御されるが、
        // プロセスとしてのUnhandled Rejectionを防ぐためにログを出して握り潰す
        logger.error(error, {
          event: LOG_EVENTS.HEALTH_CHECK.SAVE_ERROR,
          context: "HealthCheckPage.handleSave",
        });
      });
  };

  const handleFetchLatest = () => {
    void refetch();
  };

  // Aggregate states
  const isLoading = isFetching || isSaving;
  const error = saveError ?? fetchError;

  // Format date for display (Smart Component responsibility)
  const formattedCreatedAt = message?.createdAt
    ? new Date(message.createdAt).toLocaleString()
    : undefined;

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
        formattedCreatedAt={formattedCreatedAt}
      />
    </HealthCheckTemplate>
  );
};
