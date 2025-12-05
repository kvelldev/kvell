/**
 * Input Atom Tests
 *
 * Unit tests for Input component (Dumb Component).
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Input } from "@/components/atoms/Input";

describe("Input", () => {
  it("should render with value", () => {
    const handleChange = vi.fn();
    render(<Input value="test value" onChange={handleChange} />);

    const input = screen.getByRole("textbox");
    expect(input).toHaveValue("test value");
  });

  it("should call onChange when value changes", () => {
    const handleChange = vi.fn();
    render(<Input value="" onChange={handleChange} />);

    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "new value" } });

    expect(handleChange).toHaveBeenCalledWith("new value");
  });

  it("should render placeholder when provided", () => {
    const handleChange = vi.fn();
    render(
      <Input value="" onChange={handleChange} placeholder="Enter text..." />,
    );

    const input = screen.getByPlaceholderText("Enter text...");
    expect(input).toBeInTheDocument();
  });

  it("should be disabled when disabled prop is true", () => {
    const handleChange = vi.fn();
    render(<Input value="" onChange={handleChange} disabled={true} />);

    const input = screen.getByRole("textbox");
    expect(input).toBeDisabled();
  });
});
