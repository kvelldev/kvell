/**
 * SparkPostPage (Smart Component)
 *
 * Container page for posting sparks.
 * Handles business logic by connecting UseCase hooks with UI components.
 */

import { useState } from "react";
import { sparkRepository } from "@/adapter/repository/sparkRepository";
import { usePostSpark } from "@/usecase/usePostSpark";
import { SparkPostForm } from "@/components/organisms/SparkPostForm";
import { SparkPostTemplate } from "@/components/templates/SparkPostTemplate";
import { useLogger } from "@/components/useLogger";
import { settings } from "@/adapter/infra/settings";

export const SparkPostPage = () => {
  // Local UI state
  const [content, setContent] = useState("");

  // Dependency Injection: Logger
  const logger = useLogger();

  // UseCase Hook: Repository Dependency Injection
  const { postSpark, isPosting, error } = usePostSpark(sparkRepository, logger);

  // Event Handler: Submit spark
  const handleSubmit = async () => {
    const trimmedContent = content.trim();
    if (!trimmedContent) return;

    try {
      await postSpark({ content: trimmedContent });
      // On success: Clear input and navigate to timeline (future feature)
      setContent("");
      // TODO: Navigate to timeline once implemented
      // navigate("/timeline");
    } catch {
      // Error is already logged by UseCase and stored in error state
      // UI will display error via SparkPostForm
    }
  };

  return (
    <SparkPostTemplate>
      <SparkPostForm
        content={content}
        onContentChange={setContent}
        onSubmit={() => {
          void handleSubmit();
        }}
        isPosting={isPosting}
        maxLength={settings.sparkMaxLength}
        error={error}
      />
    </SparkPostTemplate>
  );
};
