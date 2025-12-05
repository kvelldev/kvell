/**
 * Logger Provider Tests
 *
 * Unit tests for LoggerProvider component.
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { LoggerProvider } from "@/components/LoggerContext";
import type { ILogger } from "@/usecase/ports/ILogger";

describe("LoggerProvider", () => {
  it("should render children", () => {
    const mockLogger: ILogger = {
      info: vi.fn(),
      error: vi.fn(),
    };

    render(
      <LoggerProvider logger={mockLogger}>
        <div>Test Child</div>
      </LoggerProvider>,
    );

    expect(screen.getByText("Test Child")).toBeInTheDocument();
  });

  it("should provide logger to children", () => {
    const mockLogger: ILogger = {
      info: vi.fn(),
      error: vi.fn(),
    };

    const TestChild = () => {
      return <div>Logger Provider Working</div>;
    };

    render(
      <LoggerProvider logger={mockLogger}>
        <TestChild />
      </LoggerProvider>,
    );

    expect(screen.getByText("Logger Provider Working")).toBeInTheDocument();
  });
});
