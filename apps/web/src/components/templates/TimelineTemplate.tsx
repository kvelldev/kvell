/**
 * Timeline Template
 *
 * Layout template for timeline page (Dumb Component).
 * Provides full-screen layout for the spark flow experience.
 */

import type { ReactNode } from "react";

interface TimelineTemplateProps {
  children: ReactNode;
}

/**
 * Timeline Template Component
 *
 * Features:
 * - Full-screen layout (100vh)
 * - Night background (bg-night-900)
 * - Proper z-index layering (z-0 for timeline content)
 * @returns Rendered timeline template layout
 */
export const TimelineTemplate = ({ children }: TimelineTemplateProps) => {
  return (
    <div className="h-screen w-screen overflow-hidden bg-night-900">
      <div className="z-0 size-full">{children}</div>
    </div>
  );
};
