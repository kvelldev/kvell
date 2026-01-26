/**
 * Logger Context
 *
 * React context for logger dependency injection.
 */

import { createContext } from "react";
import type { ILogger } from "../usecase/ports/ILogger";

/**
 * Logger Context for DI
 */
export const LoggerContext = createContext<ILogger | undefined>(undefined);
