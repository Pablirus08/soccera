import { cn } from "@/lib/utils"

type DivergingBarProps = {
  value: number
  /** Largest |value| in the set, so every row shares one scale. */
  max: number
  className?: string
}

/**
 * Bar growing right (above expectation, blue) or left (below, red) from a
 * center line. Pair it with the signed number in text: color is never the
 * only cue.
 */
export function DivergingBar({ value, max, className }: DivergingBarProps) {
  const width = max > 0 ? (Math.abs(value) / max) * 50 : 0
  return (
    <div className={cn("relative h-2.5 w-full rounded-full bg-muted", className)} aria-hidden>
      <div className="absolute inset-y-[-3px] left-1/2 w-px bg-foreground/30" />
      <div
        className={cn(
          "absolute inset-y-0",
          value >= 0 ? "left-1/2 rounded-r-full bg-diverge-pos" : "right-1/2 rounded-l-full bg-diverge-neg",
        )}
        style={{ width: `${width}%` }}
      />
    </div>
  )
}

export const signed = (v: number, digits = 1) => `${v > 0 ? "+" : ""}${v.toFixed(digits)}`
