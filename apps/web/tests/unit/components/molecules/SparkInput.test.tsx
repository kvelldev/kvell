/**
 * SparkInput Molecule Unit Test
 *
 * Tests the rendering and character counter behavior.
 * Dumb component test - validates props-based rendering logic.
 */

import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { SparkInput } from "@/components/molecules/SparkInput";
import { settings } from "@/adapter/infra/settings";

describe("SparkInput", () => {
  it("should render textarea and character counter", () => {
    const onChange = vi.fn();
    render(
      <SparkInput
        value="Test content"
        onChange={onChange}
        maxLength={settings.sparkMaxLength}
        testId="spark-input"
      />,
    );

    const textarea = screen.getByTestId("spark-input");
    expect(textarea).toBeInTheDocument();

    const counter = screen.getByTestId("spark-input-counter");
    expect(counter).toHaveTextContent(
      `12 / ${settings.sparkMaxLength.toString()}`,
    );
  });

  it("should display normal color when within limit", () => {
    const onChange = vi.fn();
    render(
      <SparkInput
        value="Short text"
        onChange={onChange}
        maxLength={settings.sparkMaxLength}
        testId="spark-input"
      />,
    );

    const counter = screen.getByTestId("spark-input-counter");
    // Should have ash color (neutral)
    expect(counter).toHaveClass("text-ash-500");
  });

  it("should display warning color when near limit (>80%)", () => {
    const onChange = vi.fn();
    // Calculate >80% of maxLength
    const nearLimitLength = Math.floor(settings.sparkMaxLength * 0.8) + 1;
    const longText = "a".repeat(nearLimitLength);

    render(
      <SparkInput
        value={longText}
        onChange={onChange}
        maxLength={settings.sparkMaxLength}
        testId="spark-input"
      />,
    );

    const counter = screen.getByTestId("spark-input-counter");
    // Should have spark color (attention)
    expect(counter).toHaveClass("text-spark-500");
  });

  it("should display error color when over limit", () => {
    const onChange = vi.fn();
    const tooLongText = "a".repeat(settings.sparkMaxLength + 1);

    render(
      <SparkInput
        value={tooLongText}
        onChange={onChange}
        maxLength={settings.sparkMaxLength}
        testId="spark-input"
      />,
    );

    const counter = screen.getByTestId("spark-input-counter");
    // Should have ember color (warning)
    expect(counter).toHaveClass("text-ember-500");
    expect(counter).toHaveTextContent(
      `${(settings.sparkMaxLength + 1).toString()} / ${settings.sparkMaxLength.toString()}`,
    );
  });

  it("should disable textarea when disabled prop is true", () => {
    const onChange = vi.fn();
    render(
      <SparkInput
        value="Test"
        onChange={onChange}
        maxLength={settings.sparkMaxLength}
        disabled={true}
        testId="spark-input"
      />,
    );

    const textarea = screen.getByTestId("spark-input");
    expect(textarea).toBeDisabled();
  });
});
