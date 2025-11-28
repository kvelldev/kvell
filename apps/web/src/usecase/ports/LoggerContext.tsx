/**
 * Logger Dependency Injection Context
 *
 * Provides logger instance throughout the application.
 * This allows dependency injection following DIP (Dependency Inversion Principle).
 */

import { createContext, useContext, type ReactNode } from "react";
import type { ILogger } from "./ILogger";

/**
 * Logger Context for DI
 */
const LoggerContext = createContext<ILogger | undefined>(undefined);

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
