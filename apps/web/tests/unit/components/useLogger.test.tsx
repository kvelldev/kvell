/**
 * useLogger Hook Tests
 *
 * Unit tests for useLogger hook.
 */

import { describe, it, expect, vi } from "vitest";
import { renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { useLogger } from "@/components/useLogger";
import { LoggerProvider } from "@/components/LoggerContext";
import type { ILogger } from "@/usecase/ports/ILogger";

describe("useLogger", () => {
  it("should return logger from context", () => {
    const mockLogger: ILogger = {
      info: vi.fn(),
      error: vi.fn(),
    };

    const wrapper = ({ children }: { children: ReactNode }) => (
      <LoggerProvider logger={mockLogger}>{children}</LoggerProvider>
    );

    const { result } = renderHook(() => useLogger(), { wrapper });

    expect(result.current).toBe(mockLogger);
  });

  it("should throw error when used outside LoggerProvider", () => {
    // Spy on console methods to suppress error logs during this test
    const errorSpy = vi.spyOn(console, "error").mockReturnValue();
    const warnSpy = vi.spyOn(console, "warn").mockReturnValue();

    expect(() => {
      renderHook(() => useLogger());
    }).toThrow("useLogger must be used within LoggerProvider");

    // Restore console methods
    errorSpy.mockRestore();
    warnSpy.mockRestore();
  });
});
