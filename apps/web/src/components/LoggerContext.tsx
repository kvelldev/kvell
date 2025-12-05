/**
 * Logger Provider Component
 *
 * Provides logger instance throughout the application.
 * This allows dependency injection following DIP (Dependency Inversion Principle).
 */

import type { ReactNode } from "react";
import type { ILogger } from "../usecase/ports/ILogger";
import { LoggerContext } from "../contexts/LoggerContext";

/**
 * Logger Provider Props
 */
interface LoggerProviderProps {
  logger: ILogger;
  children: ReactNode;
}

/**
 * Logger Provider Component
 * @param props - Provider props with logger instance
 * @param props.logger - Logger instance to provide
 * @param props.children - Child components
 * @returns Logger provider component
 */
export const LoggerProvider = ({ logger, children }: LoggerProviderProps) => {
  return (
    <LoggerContext.Provider value={logger}>{children}</LoggerContext.Provider>
  );
};
