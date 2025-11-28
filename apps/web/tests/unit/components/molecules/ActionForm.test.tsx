/**
 * ActionForm Molecule Tests
 *
 * Unit tests for ActionForm component (Dumb Component).
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ActionForm } from "@/components/molecules/ActionForm";

describe("ActionForm", () => {
  it("should render input and buttons", () => {
    const props = {
      inputValue: "",
      onInputChange: vi.fn(),
      onSave: vi.fn(),
      onFetch: vi.fn(),
      isLoading: false,
    };

    render(<ActionForm {...props} />);

    expect(
      screen.getByPlaceholderText("Enter a test message..."),
    ).toBeInTheDocument();
    expect(screen.getByText("Save to DB")).toBeInTheDocument();
    expect(screen.getByText("Fetch Latest")).toBeInTheDocument();
  });

  it("should call onInputChange when input value changes", () => {
    const handleInputChange = vi.fn();
    const props = {
      inputValue: "",
      onInputChange: handleInputChange,
      onSave: vi.fn(),
      onFetch: vi.fn(),
      isLoading: false,
    };

    render(<ActionForm {...props} />);

    const input = screen.getByPlaceholderText("Enter a test message...");
    fireEvent.change(input, { target: { value: "test" } });

    expect(handleInputChange).toHaveBeenCalledWith("test");
  });

  it("should call onSave when Save button is clicked", () => {
    const handleSave = vi.fn();
    const props = {
      inputValue: "test message",
      onInputChange: vi.fn(),
      onSave: handleSave,
      onFetch: vi.fn(),
      isLoading: false,
    };

    render(<ActionForm {...props} />);

    fireEvent.click(screen.getByText("Save to DB"));

    expect(handleSave).toHaveBeenCalledOnce();
  });

  it("should call onFetch when Fetch button is clicked", () => {
    const handleFetch = vi.fn();
    const props = {
      inputValue: "",
      onInputChange: vi.fn(),
      onSave: vi.fn(),
      onFetch: handleFetch,
      isLoading: false,
    };

    render(<ActionForm {...props} />);

    fireEvent.click(screen.getByText("Fetch Latest"));

    expect(handleFetch).toHaveBeenCalledOnce();
  });

  it("should disable Save button when input is empty", () => {
    const props = {
      inputValue: "",
      onInputChange: vi.fn(),
      onSave: vi.fn(),
      onFetch: vi.fn(),
      isLoading: false,
    };

    render(<ActionForm {...props} />);

    const saveButton = screen.getByText("Save to DB");
    expect(saveButton).toBeDisabled();
  });

  it("should disable Save button when input is whitespace only", () => {
    const props = {
      inputValue: "   ",
      onInputChange: vi.fn(),
      onSave: vi.fn(),
      onFetch: vi.fn(),
      isLoading: false,
    };

    render(<ActionForm {...props} />);

    const saveButton = screen.getByText("Save to DB");
    expect(saveButton).toBeDisabled();
  });

  it("should disable all inputs when isLoading is true", () => {
    const props = {
      inputValue: "test",
      onInputChange: vi.fn(),
      onSave: vi.fn(),
      onFetch: vi.fn(),
      isLoading: true,
    };

    render(<ActionForm {...props} />);

    expect(
      screen.getByPlaceholderText("Enter a test message..."),
    ).toBeDisabled();
    expect(screen.getByText("Save to DB")).toBeDisabled();
    expect(screen.getByText("Fetch Latest")).toBeDisabled();
  });
});
