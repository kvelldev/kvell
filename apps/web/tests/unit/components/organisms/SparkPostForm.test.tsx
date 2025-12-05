/**
 * SparkPostForm Organism Unit Test
 *
 * Tests the complete form rendering and interaction logic.
 * Dumb component test - validates all props-based behavior.
 */

import { render, screen } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { SparkPostForm } from "@/components/organisms/SparkPostForm";
import { settings } from "@/adapter/infra/settings";

describe("SparkPostForm", () => {
  it("should render form with input and submit button", () => {
    const onContentChange = vi.fn();
    const onSubmit = vi.fn();

    render(
      <SparkPostForm
        content=""
        onContentChange={onContentChange}
        onSubmit={onSubmit}
        isPosting={false}
        maxLength={settings.sparkMaxLength}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "種火を投げる" }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("spark-input")).toBeInTheDocument();
    expect(screen.getByTestId("spark-submit-button")).toBeInTheDocument();
  });

  it("should disable submit button when content is empty", () => {
    const onContentChange = vi.fn();
    const onSubmit = vi.fn();

    render(
      <SparkPostForm
        content=""
        onContentChange={onContentChange}
        onSubmit={onSubmit}
        isPosting={false}
        maxLength={settings.sparkMaxLength}
      />,
    );

    const submitButton = screen.getByTestId("spark-submit-button");
    expect(submitButton).toBeDisabled();
  });

  it("should disable submit button when content is only whitespace", () => {
    const onContentChange = vi.fn();
    const onSubmit = vi.fn();

    render(
      <SparkPostForm
        content="   "
        onContentChange={onContentChange}
        onSubmit={onSubmit}
        isPosting={false}
        maxLength={settings.sparkMaxLength}
      />,
    );

    const submitButton = screen.getByTestId("spark-submit-button");
    expect(submitButton).toBeDisabled();
  });

  it("should disable submit button when content is over limit", () => {
    const onContentChange = vi.fn();
    const onSubmit = vi.fn();
    const tooLongContent = "a".repeat(settings.sparkMaxLength + 1);

    render(
      <SparkPostForm
        content={tooLongContent}
        onContentChange={onContentChange}
        onSubmit={onSubmit}
        isPosting={false}
        maxLength={settings.sparkMaxLength}
      />,
    );

    const submitButton = screen.getByTestId("spark-submit-button");
    expect(submitButton).toBeDisabled();
  });

  it("should enable submit button when content is valid", () => {
    const onContentChange = vi.fn();
    const onSubmit = vi.fn();

    render(
      <SparkPostForm
        content="Valid spark content"
        onContentChange={onContentChange}
        onSubmit={onSubmit}
        isPosting={false}
        maxLength={settings.sparkMaxLength}
      />,
    );

    const submitButton = screen.getByTestId("spark-submit-button");
    expect(submitButton).not.toBeDisabled();
  });

  it("should call onSubmit when submit button is clicked", async () => {
    const user = userEvent.setup();
    const onContentChange = vi.fn();
    const onSubmit = vi.fn();

    render(
      <SparkPostForm
        content="Valid content"
        onContentChange={onContentChange}
        onSubmit={onSubmit}
        isPosting={false}
        maxLength={settings.sparkMaxLength}
      />,
    );

    const submitButton = screen.getByTestId("spark-submit-button");
    await user.click(submitButton);

    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  it("should disable all inputs when isPosting is true", () => {
    const onContentChange = vi.fn();
    const onSubmit = vi.fn();

    render(
      <SparkPostForm
        content="Valid content"
        onContentChange={onContentChange}
        onSubmit={onSubmit}
        isPosting={true}
        maxLength={settings.sparkMaxLength}
      />,
    );

    expect(screen.getByTestId("spark-input")).toBeDisabled();
    expect(screen.getByTestId("spark-submit-button")).toBeDisabled();
    expect(screen.getByTestId("spark-submit-button")).toHaveTextContent(
      "投稿中...",
    );
  });

  it("should display error message when error prop is provided", () => {
    const onContentChange = vi.fn();
    const onSubmit = vi.fn();
    const error = new Error("Test error message");

    render(
      <SparkPostForm
        content="Valid content"
        onContentChange={onContentChange}
        onSubmit={onSubmit}
        isPosting={false}
        maxLength={settings.sparkMaxLength}
        error={error}
      />,
    );

    const errorElement = screen.getByTestId("spark-error");
    expect(errorElement).toBeInTheDocument();
    expect(errorElement).toHaveTextContent("エラー: Test error message");
  });

  it("should not display error message when error is null", () => {
    const onContentChange = vi.fn();
    const onSubmit = vi.fn();

    render(
      <SparkPostForm
        content="Valid content"
        onContentChange={onContentChange}
        onSubmit={onSubmit}
        isPosting={false}
        maxLength={settings.sparkMaxLength}
        error={null}
      />,
    );

    expect(screen.queryByTestId("spark-error")).not.toBeInTheDocument();
  });
});
