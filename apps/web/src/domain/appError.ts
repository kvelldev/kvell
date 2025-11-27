import { internalStatuses, InternalStatusCodes } from "@/domain/constants";

export default class AppError extends Error {
  public override cause?: Error;
  public context?: Record<string, unknown>;
  constructor(
    public status: InternalStatusCodes,
    message?: string,
    options?: {
      cause?: Error;
      context?: Record<string, unknown>;
    },
  ) {
    super(message ?? internalStatuses[status]);
    this.name = "AppError";
    this.status = status;

    Object.setPrototypeOf(this, AppError.prototype);

    if (options?.cause instanceof Error) {
      this.cause = options.cause;
    }
    if (options?.context) {
      this.context = options.context;
    }
  }
}
