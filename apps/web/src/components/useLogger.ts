/**
 * useLogger Hook
 *
 * Custom hook to access logger instance from context.
 */

import { useContext } from "react";
import type { ILogger } from "../usecase/ports/ILogger";
import { LoggerContext } from "../contexts/LoggerContext";

/**
 * Hook to access logger instance
 * @returns Logger instance
 * @throws {Error} If used outside LoggerProvider
 */
export const useLogger = (): ILogger => {
  const logger = useContext(LoggerContext);
  if (!logger) {
    throw new Error("useLogger must be used within LoggerProvider");
  }
  return logger;
};
