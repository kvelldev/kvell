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
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        {children}
      </div>
    </div>
  );
};
