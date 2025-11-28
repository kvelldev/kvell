/**
 * HealthCheckTemplate Tests
 *
 * Unit tests for HealthCheckTemplate component (Dumb Component).
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { HealthCheckTemplate } from "@/components/templates/HealthCheckTemplate";

describe("HealthCheckTemplate", () => {
  it("should render children", () => {
    render(
      <HealthCheckTemplate>
        <div>Test Content</div>
      </HealthCheckTemplate>,
    );

    expect(screen.getByText("Test Content")).toBeInTheDocument();
  });

  it("should apply layout classes", () => {
    const { container } = render(
      <HealthCheckTemplate>
        <div>Test</div>
      </HealthCheckTemplate>,
    );

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("min-h-screen");
    expect(wrapper.className).toContain("bg-gray-50");
  });
});
