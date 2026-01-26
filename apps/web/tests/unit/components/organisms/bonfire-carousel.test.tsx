import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { BonfireCarousel } from "@/components/organisms/BonfireCarousel";
import { BonfireViewModel } from "@/domain/model/bonfire";

// Mock child components to isolate tests
vi.mock("@/components/molecules/BonfireCard", () => ({
  BonfireCard: ({
    bonfire,
    onClick,
  }: {
    bonfire: BonfireViewModel;
    onClick?: (b: BonfireViewModel) => void;
  }) => (
    <div data-testid="bonfire-card" onClick={() => onClick?.(bonfire)}>
      {bonfire.content}
    </div>
  ),
}));

vi.mock("@/components/molecules/BonfirePlaceholderCard", () => ({
  BonfirePlaceholderCard: ({ message }: { message: string }) => (
    <div data-testid="bonfire-placeholder">{message}</div>
  ),
}));

// Mock Carousel components
vi.mock("@/components/ui/carousel", () => ({
  Carousel: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  CarouselContent: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  CarouselItem: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  CarouselPrevious: () => <button>Prev</button>,
  CarouselNext: () => <button>Next</button>,
}));

describe("BonfireCarousel", () => {
  const mockBonfire: BonfireViewModel = {
    id: "bonfire-1",
    sparkId: "spark-1",
    fieldId: "test-field",
    content: "Test Bonfire",
    uniqueUserCount: 5,
    heatScore: 100,
    createdAt: new Date().toISOString(),
    decayAt: new Date().toISOString(),
  } as unknown as BonfireViewModel;

  it("renders only generic placeholder when bonfires list is empty", () => {
    render(<BonfireCarousel bonfires={[]} />);

    expect(screen.getByTestId("bonfire-placeholder")).toBeInTheDocument();
    expect(screen.queryByTestId("bonfire-card")).not.toBeInTheDocument();
  });

  it("renders bonfires and appends placeholder at the end when list is not empty", () => {
    const bonfires = [
      { ...mockBonfire, id: "1", content: "B1" },
      { ...mockBonfire, id: "2", content: "B2" },
    ];

    render(<BonfireCarousel bonfires={bonfires} />);

    const cards = screen.getAllByTestId("bonfire-card");
    expect(cards).toHaveLength(2);
    expect(cards[0]).toHaveTextContent("B1");
    expect(cards[1]).toHaveTextContent("B2");

    expect(screen.getByTestId("bonfire-placeholder")).toBeInTheDocument();
  });
});
