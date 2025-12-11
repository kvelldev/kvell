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
    <div className="flex min-h-screen items-center justify-center p-4">
      {children}
    </div>
  );
};
