/**
 * Textarea Atom Unit Test
 *
 * Tests the rendering and behavior of the Textarea component.
 * Dumb component test - no hooks or context mocking needed.
 */

import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { Textarea } from "@/components/atoms/Textarea";

describe("Textarea", () => {
  it("should render with value and placeholder", () => {
    const onChange = vi.fn();
    render(
      <Textarea
        value="Test content"
        onChange={onChange}
        placeholder="Enter text..."
        testId="test-textarea"
      />,
    );

    const textarea = screen.getByRole("textbox");
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveValue("Test content");
    expect(textarea).toHaveAttribute("placeholder", "Enter text...");
  });

  it("should call onChange when text is entered", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();

    render(<Textarea value="" onChange={onChange} testId="test-textarea" />);

    const textarea = screen.getByTestId("test-textarea");
    await user.type(textarea, "New text");

    // onChange should be called for each character typed
    expect(onChange).toHaveBeenCalled();
    expect(onChange).toHaveBeenCalledWith("N");
  });

  it("should be disabled when disabled prop is true", () => {
    const onChange = vi.fn();
    render(
      <Textarea
        value="Test"
        onChange={onChange}
        disabled={true}
        testId="test-textarea"
      />,
    );

    const textarea = screen.getByTestId("test-textarea");
    expect(textarea).toBeDisabled();
  });

  it("should respect maxLength prop", () => {
    const onChange = vi.fn();
    render(
      <Textarea
        value="Test"
        onChange={onChange}
        maxLength={10}
        testId="test-textarea"
      />,
    );

    const textarea = screen.getByRole("textbox");
    expect(textarea).toHaveAttribute("maxLength", "10");
  });
});
