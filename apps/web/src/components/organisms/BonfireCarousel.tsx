/**
 * BonfireCarousel Organism Component (Dumb)
 *
 * Horizontally scrolling container for bonfires using shadcn Carousel.
 * Pure presentational component - receives all data via props.
 *
 * UX Design:
 * - Mobile: Swipe/drag only (buttons hidden)
 * - Desktop: Swipe/drag + hover-visible buttons
 *
 * Visual style follows Design Token guidelines.
 * Uses shadcn/ui Carousel (Embla) as base component.
 */

import type { Bonfire } from "@/domain/model/bonfire";
import { BonfireCard } from "@/components/molecules/BonfireCard";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
} from "@/components/ui/carousel";

/**
 * Props for BonfireCarousel component
 */
interface BonfireCarouselProps {
  /**
   * Array of bonfires to display
   */
  bonfires: Bonfire[];
  /**
   * Callback when a bonfire card is clicked
   */
  onBonfireClick?: (bonfire: Bonfire) => void;
}

/**
 * BonfireCarousel Component
 *
 * Features:
 * - Horizontal carousel with Embla (via shadcn)
 * - Responsive navigation: hidden on mobile, hover-visible on desktop
 * - Drag/swipe support on all devices
 * - Empty state returns null (no bonfires = no carousel)
 * @returns Rendered carousel element or null if empty
 */
export const BonfireCarousel = ({
  bonfires,
  onBonfireClick,
}: BonfireCarouselProps) => {
  // Empty State: Return null when no bonfires are available
  if (bonfires.length === 0) {
    return null;
  }

  return (
    <section
      className="group relative w-full px-4 py-4 md:px-12"
      data-testid="bonfire-carousel"
      aria-label="焚き火エリア"
    >
      <Carousel
        opts={{
          align: "center",
          loop: false,
          dragFree: false,
        }}
        className="w-full"
      >
        <CarouselContent className="-ml-4 overflow-visible">
          {bonfires.map((bonfire) => (
            <CarouselItem key={bonfire.id} className="basis-auto py-4 pl-4">
              <BonfireCard bonfire={bonfire} onClick={onBonfireClick} />
            </CarouselItem>
          ))}
        </CarouselContent>

        {/* Navigation buttons: hidden on mobile, hover-visible on desktop */}
        <CarouselPrevious className="left-2 hidden h-12 w-12 opacity-0 transition-opacity duration-300 group-hover:opacity-100 md:flex" />
        <CarouselNext className="right-2 hidden h-12 w-12 opacity-0 transition-opacity duration-300 group-hover:opacity-100 md:flex" />
      </Carousel>
    </section>
  );
};
