import * as React from "react"

import { cn } from "@/lib/utils"

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.ComponentProps<"textarea">
>(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "flex min-h-[80px] w-full rounded-card border border-white/10 bg-night-800/40 backdrop-blur-md px-4 py-3 text-sm text-smoke-100 placeholder:text-ash-500 resize-none focus:outline-none focus:shadow-glow-sm transition-all disabled:cursor-not-allowed disabled:opacity-50 font-base font-light",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Textarea.displayName = "Textarea"

export { Textarea }
