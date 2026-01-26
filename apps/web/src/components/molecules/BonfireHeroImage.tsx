import { useState } from "react";

import { motion } from "framer-motion";
import { LightboxModal } from "@/components/molecules/LightboxModal";
import defaultImage from "@/assets/bonfire_default.png";

interface BonfireHeroImageProps {
  bonfireId: string;
  image?: {
    primaryUrl: string;
    fallbackUrl?: string;
  };
}

/**
 * BonfireHeroImage
 *
 * Renders the hero image for the Bonfire Detail Header.
 * Handles:
 * - Background blur effect
 * - Foreground main image
 * - Fallback logic on error
 * - Lightbox expansion
 *
 * NOTE: This component manages its own 'currentSrc' state.
 * To reset state when the image URL changes (e.g. navigation),
 * the parent MUST provide a `key` prop unique to the image URL.
 * @returns Refactored Bonfire Hero Image component
 */
export const BonfireHeroImage = ({
  bonfireId,
  image,
}: BonfireHeroImageProps) => {
  const primaryUrl = image?.primaryUrl;
  const fallbackUrl = image?.fallbackUrl;

  const [currentSrc, setCurrentSrc] = useState(primaryUrl);
  const [hasError, setHasError] = useState(false);

  // If no image is provided, or we've encountered an error that exhausted fallbacks
  const showCustomImage = !!currentSrc && !hasError;

  const handleError = () => {
    if (currentSrc === primaryUrl && fallbackUrl) {
      setCurrentSrc(fallbackUrl);
    } else {
      setHasError(true);
    }
  };

  return (
    <motion.div
      className="absolute inset-0 overflow-hidden bg-black/40"
      layoutId={`bonfire-image-${bonfireId}`}
    >
      {showCustomImage ? (
        <>
          {/* Background: Blur & Cover */}
          <img
            src={currentSrc}
            alt=""
            className="absolute inset-0 h-full w-full object-cover opacity-50 blur-xl"
            aria-hidden="true"
          />
          {/* Foreground: Contain & Clear */}
          <div className="relative h-full w-full">
            {/* Note: currentSrc is guaranteed to be defined here due to showCustomImage check */}
            <LightboxModal src={currentSrc}>
              <div className="h-full w-full cursor-zoom-in">
                <img
                  src={currentSrc}
                  alt="Bonfire"
                  className="h-full w-full object-contain transition-transform duration-500 hover:scale-105"
                  onError={handleError}
                />
              </div>
            </LightboxModal>
          </div>
        </>
      ) : (
        <img
          src={defaultImage}
          alt="Bonfire Default"
          className="h-full w-full object-cover"
        />
      )}
    </motion.div>
  );
};
