/**
 * Button Atom Tests
 *
 * Unit tests for Button component (Dumb Component).
 */

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Button } from "@/components/atoms/Button";

describe("Button", () => {
  it("should render children correctly", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);

    expect(screen.getByRole("button")).toHaveTextContent("Click Me");
  });

  it("should call onClick when clicked", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);

    fireEvent.click(screen.getByRole("button"));

    expect(handleClick).toHaveBeenCalledOnce();
  });

  it("should be disabled when disabled prop is true", () => {
    const handleClick = vi.fn();
    render(
      <Button onClick={handleClick} disabled={true}>
        Click Me
      </Button>,
    );

    const button = screen.getByRole("button");
    expect(button).toBeDisabled();

    fireEvent.click(button);
    expect(handleClick).not.toHaveBeenCalled();
  });

  it("should render with primary variant by default", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);

    const button = screen.getByRole("button");
    expect(button.className).toContain("bg-ember-500");
  });

  it("should render with secondary variant when specified", () => {
    const handleClick = vi.fn();
    render(
      <Button onClick={handleClick} variant="secondary">
        Click Me
      </Button>,
    );

    const button = screen.getByRole("button");
    expect(button.className).toContain("bg-night-800");
  });
});
