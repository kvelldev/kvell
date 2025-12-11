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
    <div className="flex h-screen w-screen flex-col overflow-hidden">
      <div className="text-ash-500 flex h-40 flex-none items-center justify-center border-2 backdrop-blur-md">
        Here is a prepared area for bonfire.
      </div>
      <main className="z-0 min-h-0 w-full flex-1">{children}</main>
    </div>
  );
};
