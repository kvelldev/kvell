/**
 * MessageViewer Molecule Tests
 *
 * Unit tests for MessageViewer component (Dumb Component).
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MessageViewer } from "@/components/molecules/MessageViewer";
import type { HealthMessage } from "@/domain/model/health";

describe("MessageViewer", () => {
  it("should display loading state", () => {
    render(<MessageViewer message={null} isLoading={true} error={undefined} />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("should display error state", () => {
    const error = new Error("Network error");
    render(<MessageViewer message={null} isLoading={false} error={error} />);

    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.getByText("Network error")).toBeInTheDocument();
  });

  it("should display success state with message", () => {
    const message: HealthMessage = {
      id: "123",
      message: "Test message",
      createdAt: "2024-01-01T00:00:00Z",
    };

    render(
      <MessageViewer message={message} isLoading={false} error={undefined} />,
    );

    expect(screen.getByText("Success")).toBeInTheDocument();
    expect(screen.getByText(/Test message/)).toBeInTheDocument();
    expect(screen.getByText(/ID: 123/)).toBeInTheDocument();
  });

  it("should render nothing when no message and no error", () => {
    const { container } = render(
      <MessageViewer message={null} isLoading={false} error={undefined} />,
    );

    expect(container.firstChild).toBeNull();
  });

  it("should prioritize loading over error", () => {
    const error = new Error("Test error");
    render(<MessageViewer message={null} isLoading={true} error={error} />);

    expect(screen.getByText("Loading...")).toBeInTheDocument();
    expect(screen.queryByText("Error")).not.toBeInTheDocument();
  });

  it("should prioritize error over message", () => {
    const message: HealthMessage = {
      id: "123",
      message: "Test message",
      createdAt: "2024-01-01T00:00:00Z",
    };
    const error = new Error("Test error");

    render(<MessageViewer message={message} isLoading={false} error={error} />);

    expect(screen.getByText("Error")).toBeInTheDocument();
    expect(screen.queryByText("Success")).not.toBeInTheDocument();
  });
});
