import * as Sentry from "@sentry/react";
import { ILogger } from "@/usecase/ports/ILogger";

export class SentryLogger implements ILogger {
  info(message: string, context?: Record<string, unknown>) {
    // ... implementation
  }
  error(error: unknown, context?: Record<string, unknown>) {
    // ... implementation
    Sentry.captureException(error);
  }
}
