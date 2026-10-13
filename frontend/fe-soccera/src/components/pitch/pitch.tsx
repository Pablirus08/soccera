import type { ReactNode } from "react"

import { cn } from "@/lib/utils"

// Pitch drawn in meters (105 x 68) so markings use real dimensions.
export const PITCH_LENGTH = 105
export const PITCH_WIDTH = 68

const line = { fill: "none", stroke: "var(--pitch-line)", strokeWidth: 0.35 }

/** Markings for one half, attacking goal at y = 0 (top of a vertical half pitch). */
function HalfMarkings() {
  const w = PITCH_WIDTH
  return (
    <g {...line}>
      <rect x={0} y={0} width={w} height={PITCH_LENGTH / 2} />
      <rect x={(w - 40.32) / 2} y={0} width={40.32} height={16.5} />
      <rect x={(w - 18.32) / 2} y={0} width={18.32} height={5.5} />
      <rect x={(w - 7.32) / 2} y={-1.5} width={7.32} height={1.5} />
      <circle cx={w / 2} cy={11} r={0.4} fill="var(--pitch-line)" />
      {/* Arc of the box: the part of the 9.15 m circle outside the area. */}
      <path d={`M ${w / 2 - 7.31} 16.5 A 9.15 9.15 0 0 0 ${w / 2 + 7.31} 16.5`} />
      <path d={`M ${w / 2 - 9.15} ${PITCH_LENGTH / 2} A 9.15 9.15 0 0 1 ${w / 2 + 9.15} ${PITCH_LENGTH / 2}`} />
    </g>
  )
}

/** Vertical half pitch (attacking upward); children use the same meter coordinates. */
export function HalfPitch({ children, className }: { children?: ReactNode; className?: string }) {
  return (
    <svg
      viewBox={`-2 -3 ${PITCH_WIDTH + 4} ${PITCH_LENGTH / 2 + 5}`}
      className={cn("w-full rounded-lg bg-[var(--pitch-bg)]", className)}
      role="img"
    >
      <HalfMarkings />
      {children}
    </svg>
  )
}

/** Horizontal full pitch, attacking to the right; children use meter coordinates. */
export function FullPitch({ children, className }: { children?: ReactNode; className?: string }) {
  const L = PITCH_LENGTH
  const W = PITCH_WIDTH
  return (
    <svg viewBox={`-3 -2 ${L + 6} ${W + 4}`} className={cn("w-full rounded-lg bg-[var(--pitch-bg)]", className)} role="img">
      {children}
      <g {...line}>
        <rect x={0} y={0} width={L} height={W} />
        <line x1={L / 2} y1={0} x2={L / 2} y2={W} />
        <circle cx={L / 2} cy={W / 2} r={9.15} />
        <rect x={0} y={(W - 40.32) / 2} width={16.5} height={40.32} />
        <rect x={L - 16.5} y={(W - 40.32) / 2} width={16.5} height={40.32} />
        <rect x={0} y={(W - 18.32) / 2} width={5.5} height={18.32} />
        <rect x={L - 5.5} y={(W - 18.32) / 2} width={5.5} height={18.32} />
        <rect x={-1.5} y={(W - 7.32) / 2} width={1.5} height={7.32} />
        <rect x={L} y={(W - 7.32) / 2} width={1.5} height={7.32} />
      </g>
    </svg>
  )
}
