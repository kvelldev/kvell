export interface ILogger {
  info(message: string, context?: Record<string, unknown>): void;
  error(error: unknown, context?: Record<string, unknown>): void;
}
