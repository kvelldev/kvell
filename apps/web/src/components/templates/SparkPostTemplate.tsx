/**
 * SparkPostTemplate Template
 *
 * Layout template for spark posting page.
 * Provides consistent spacing and background.
 */

interface SparkPostTemplateProps {
  children: React.ReactNode;
}

export const SparkPostTemplate = ({ children }: SparkPostTemplateProps) => {
  return (
    <div className="min-h-screen bg-night-900 flex items-center justify-center p-4">
      {children}
    </div>
  );
};
