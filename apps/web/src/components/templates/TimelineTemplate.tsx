/**
 * Timeline Template
 *
 * Layout template for timeline page (Dumb Component).
 * Provides full-screen layout for the spark flow experience.
 */

import type { ReactNode } from "react";

interface TimelineTemplateProps {
  /**
   * Content for the spark timeline area (main content)
   */
  sparkArea: ReactNode;
  /**
   * Content for the bonfire carousel area (top section)
   */
  bonfireArea?: ReactNode;
}

/**
 * Timeline Template Component
 *
 * Features:
 * - Full-screen layout (100vh)
 * - Proper z-index layering (z-0 for timeline content)
 * @returns Rendered timeline template layout
 */
export const TimelineTemplate = ({
  sparkArea,
  bonfireArea,
}: TimelineTemplateProps) => {
  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden">
      <div className="z-10 flex-none">{bonfireArea}</div>
      <main className="z-0 min-h-0 w-full flex-1">{sparkArea}</main>
    </div>
  );
};
