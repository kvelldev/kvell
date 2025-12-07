/**
 * Health Check Template
 *
 * Layout template for health check page (Dumb Component).
 * Defines the page structure without specific styling or logic.
 */

import type { ReactNode } from "react";

interface HealthCheckTemplateProps {
  children: ReactNode;
}

export const HealthCheckTemplate = ({ children }: HealthCheckTemplateProps) => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-night-900 p-4">
      <div className="w-full max-w-md rounded-card bg-night-800 p-6 shadow-glow-md">
        {children}
      </div>
    </div>
  );
};
