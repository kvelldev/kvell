/**
 * HealthCheckMonitor Organism Tests
 *
 * Unit tests for HealthCheckMonitor component (Dumb Component).
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { HealthCheckMonitor } from "@/components/organisms/HealthCheckMonitor";
import type { HealthMessage } from "@/domain/model/health";

describe("HealthCheckMonitor", () => {
  const defaultProps = {
    inputValue: "",
    onInputChange: vi.fn(),
    onSave: vi.fn(),
    onFetch: vi.fn(),
    message: null,
    isLoading: false,
    error: undefined,
  };

  it("should render title and child components", () => {
    render(<HealthCheckMonitor {...defaultProps} />);

    expect(screen.getByText("System Health Check")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Enter a test message..."),
    ).toBeInTheDocument();
    expect(screen.getByText("Save to DB")).toBeInTheDocument();
    expect(screen.getByText("Fetch Latest")).toBeInTheDocument();
  });

  it("should pass props correctly to ActionForm", () => {
    const handleInputChange = vi.fn();
    const handleSave = vi.fn();
    const handleFetch = vi.fn();

    const props = {
      ...defaultProps,
      inputValue: "test input",
      onInputChange: handleInputChange,
      onSave: handleSave,
      onFetch: handleFetch,
    };

    render(<HealthCheckMonitor {...props} />);

    const input = screen.getByPlaceholderText("Enter a test message...");
    expect(input).toHaveValue("test input");

    fireEvent.change(input, { target: { value: "new value" } });
    expect(handleInputChange).toHaveBeenCalledWith("new value");

    fireEvent.click(screen.getByText("Save to DB"));
    expect(handleSave).toHaveBeenCalledOnce();

    fireEvent.click(screen.getByText("Fetch Latest"));
    expect(handleFetch).toHaveBeenCalledOnce();
  });

  it("should display loading state", () => {
    const props = {
      ...defaultProps,
      isLoading: true,
    };

    render(<HealthCheckMonitor {...props} />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("should display error state", () => {
    const props = {
      ...defaultProps,
      error: new Error("Test error"),
    };

    render(<HealthCheckMonitor {...props} />);

    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.getByText("Test error")).toBeInTheDocument();
  });

  it("should display success state with message", () => {
    const message: HealthMessage = {
      id: "123",
      message: "Hello World",
      createdAt: "2024-01-01T00:00:00Z",
    };

    const props = {
      ...defaultProps,
      message,
    };

    render(<HealthCheckMonitor {...props} />);

    expect(screen.getByText("Success")).toBeInTheDocument();
    expect(screen.getByText(/Hello World/)).toBeInTheDocument();
  });
});
