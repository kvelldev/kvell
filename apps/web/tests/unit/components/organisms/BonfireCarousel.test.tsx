import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { BonfireCarousel } from "@/components/organisms/BonfireCarousel";
import { BonfireViewModel } from "@/domain/model/bonfire";

// Mock child components to isolate tests
vi.mock("@/components/molecules/BonfireCard", () => ({
  BonfireCard: ({ bonfire, onClick }: { bonfire: any; onClick?: any }) => (
    <div data-testid="bonfire-card" onClick={() => onClick && onClick(bonfire)}>
      {bonfire.title}
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
    title: "Test Bonfire",
    sparkCount: 5,
    expiresAt: new Date(),
    isLit: true,
  } as unknown as BonfireViewModel;

  it("renders only generic placeholder when bonfires list is empty", () => {
    render(<BonfireCarousel bonfires={[]} />);

    expect(screen.getByTestId("bonfire-placeholder")).toBeInTheDocument();
    expect(screen.queryByTestId("bonfire-card")).not.toBeInTheDocument();
  });

  it("renders bonfires and appends placeholder at the end when list is not empty", () => {
    const bonfires = [
      { ...mockBonfire, id: "1", title: "B1" },
      { ...mockBonfire, id: "2", title: "B2" },
    ];

    render(<BonfireCarousel bonfires={bonfires} />);

    const cards = screen.getAllByTestId("bonfire-card");
    expect(cards).toHaveLength(2);
    expect(cards[0]).toHaveTextContent("B1");
    expect(cards[1]).toHaveTextContent("B2");

    expect(screen.getByTestId("bonfire-placeholder")).toBeInTheDocument();
  });
});
