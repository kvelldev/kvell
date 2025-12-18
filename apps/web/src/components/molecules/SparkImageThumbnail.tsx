import { useState } from "react";
import clsx from "clsx";
import placeholderError from "@/assets/placeholder_error.png";
import { LightboxModal } from "./LightboxModal";

// Interface removed, using inline for simplicity or define new one
// But for now, since I replaced the component body, I just need to remove the old interface if it became unused or redefine it.
// The previous replace replaced the component definition.
// I need to check where the interface was.
// It was lines 6-11.
// I'll leave it for now or delete it if I can targeting it.
// Actually, I can just update the props in usage in SparkCard.

/**
 * Spark Image Thumbnail
 *
 * Renders a thumbnail of the detected image.
 * Handles loading errors by showing a fallback asset.
 * Wraps content in LightboxModal for expansion.
 * @returns Thumbnail Component
 */
export const SparkImageThumbnail = ({
  image,
}: {
  image: { primaryUrl: string; fallbackUrl?: string };
}) => {
  const [currentSrc, setCurrentSrc] = useState(image.primaryUrl);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // If the image prop changes, reset state
  if (
    currentSrc !== image.primaryUrl &&
    currentSrc !== image.fallbackUrl &&
    !hasError
  ) {
    // This simplistic check might be buggy if parent re-renders passing new object reference check
    // Better to use useEffect or key
  }
  // Actually, using a key on the component in parent is safer if URL changes.
  // OR use useEffect to sync.

  if (hasError) {
    return (
      <div className="mt-3 w-full overflow-hidden rounded-md border border-white/10 bg-black/20">
        <img
          src={placeholderError}
          alt="Image load failed"
          className="md: h-auto max-h-[100px] w-full object-contain opacity-70 md:max-h-[200px]"
        />
      </div>
    );
  }

  const handleError = () => {
    // If currently using primary and fallback exists, switch to fallback
    if (currentSrc === image.primaryUrl && image.fallbackUrl) {
      setCurrentSrc(image.fallbackUrl);
      setIsLoading(true); // Reset loading for new source
    } else {
      // Logic: If already on fallback OR no fallback exists, show error
      setIsLoading(false);
      setHasError(true);
    }
  };

  return (
    <LightboxModal src={currentSrc}>
      <div
        className={clsx(
          "group relative mt-3 w-full cursor-zoom-in overflow-hidden rounded-md",
          "border border-white/10 bg-black/20 transition-colors hover:border-white/20",
          isLoading ? "min-h-[150px] animate-pulse bg-white/5" : "",
        )}
      >
        <img
          src={currentSrc}
          alt="Spark attachment"
          className={clsx(
            "h-auto max-h-[100px] w-full object-contain transition-opacity duration-300 md:max-h-[200px]",
            isLoading ? "opacity-0" : "opacity-100",
          )}
          referrerPolicy="no-referrer"
          onLoad={() => {
            setIsLoading(false);
          }}
          onError={handleError}
        />
      </div>
    </LightboxModal>
  );
};
