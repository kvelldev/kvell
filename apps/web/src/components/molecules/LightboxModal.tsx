import {
  Dialog,
  DialogContent,
  DialogTrigger,
  DialogTitle,
} from "@/components/ui/dialog";
import { ExternalLink } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

interface LightboxModalProps {
  /**
   * Source URL of the image
   */
  src: string;
  /**
   * Children to act as trigger (Thumbnail)
   */
  children: React.ReactNode;
}

/**
 * Lightbox Modal
 *
 * Expands the image to full screen (within modal)
 * Uses shadcn/ui Dialog
 * @returns Lightbox Modal Component
 */
export const LightboxModal = ({ src, children }: LightboxModalProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent
        className="bg-night-900/50 max-w-5xl rounded-md border border-white/10 p-0 shadow-none backdrop-blur-md sm:max-w-5xl"
        // Hide default close button to use custom overlay click or custom button if needed
        // but shadcn DialogContent has close button by default.
        // We want a clean look.
      >
        <DialogTitle className="sr-only">Image Preview</DialogTitle>
        <div className="relative flex min-h-[50vh] flex-col items-center justify-center p-4">
          {/* Image Container */}
          <div className="relative">
            <img
              src={src}
              alt="Expanded preview"
              className={clsx(
                "max-h-[85vh] w-auto max-w-full object-contain shadow-2xl",
                "animate-in fade-in zoom-in-95 duration-300",
              )}
              referrerPolicy="no-referrer"
            />
            {/* Source Link Icon (floating bottom right of image) */}
            <a
              href={src}
              target="_blank"
              rel="noopener noreferrer"
              className={clsx(
                "rounded-button absolute right-4 bottom-4 flex items-center gap-1.5",
                "bg-night-900/60 px-3 py-1.5 text-xs text-white/90 backdrop-blur-sm",
                "transition-colors hover:bg-black/80 hover:text-white",
              )}
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              <ExternalLink className="h-3.5 w-3.5" />
              <span>Original</span>
            </a>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
