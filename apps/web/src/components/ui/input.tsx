import * as React from "react"

import { cn } from "@/lib/utils"

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-card border border-white/10 bg-night-800/40 backdrop-blur-md px-4 py-2 text-sm text-smoke-100 placeholder:text-ash-500 focus:outline-none focus:shadow-glow-sm transition-all disabled:cursor-not-allowed disabled:opacity-50 font-base font-light",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }
