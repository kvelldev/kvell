/**
 * Sentry Logger Implementation
 *
 * Adapter layer implementation of ILogger using Sentry.
 */

import * as Sentry from "@sentry/react";
import type { ILogger } from "@/usecase/ports/ILogger";

/**
 * Type guard to check if Sentry has captureMessage
 * @param target - The object to check
 * @returns True if target has captureMessage method
 */
const hasCaptureMessage = (
  target: unknown,
): target is {
  captureMessage: (message: string, options?: unknown) => void;
} => {
  return (
    typeof target === "object" &&
    target !== null &&
    "captureMessage" in target &&
    typeof (target as Record<string, unknown>).captureMessage === "function"
  );
};

/**
 * Type guard to check if Sentry has captureException
 * @param target - The object to check
 * @returns True if target has captureException method
 */
const hasCaptureException = (
  target: unknown,
): target is {
  captureException: (error: unknown, options?: unknown) => void;
} => {
  return (
    typeof target === "object" &&
    target !== null &&
    "captureException" in target &&
    typeof (target as Record<string, unknown>).captureException === "function"
  );
};

/**
 * Logger implementation using Sentry for error tracking
 */
export class SentryLogger implements ILogger {
  info(message: string, context?: Record<string, unknown>): void {
    console.info(message, context);
    if (hasCaptureMessage(Sentry)) {
      Sentry.captureMessage(message, {
        level: "info",
        extra: context,
      });
    }
  }

  error(error: unknown, context?: Record<string, unknown>): void {
    console.error(error, context);
    if (hasCaptureException(Sentry)) {
      Sentry.captureException(error, {
        extra: context,
      });
    }
  }
}

/**
 * Singleton instance of SentryLogger
 */
export const sentryLogger = new SentryLogger();
