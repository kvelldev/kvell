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
    <div className="min-h-screen bg-night-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-night-800 rounded-card shadow-glow-md p-6">
        {children}
      </div>
    </div>
  );
};
