import { cn } from "@/lib/utils"

// Same slot order everywhere a home/draw/away split appears.
export const OUTCOME_COLORS = {
  home: "var(--chart-1)",
  draw: "var(--chart-3)",
  away: "var(--chart-2)",
}

type OutcomeBarProps = {
  home: number // 0-1
  draw: number
  away: number
  labels?: [string, string, string]
  className?: string
}

const pct = (v: number) => `${Math.round(v * 100)}%`

/**
 * Three-segment probability bar with the percentages printed inside (and
 * in each segment's title), so it never depends on color alone.
 */
export function OutcomeBar({ home, draw, away, labels = ["Local", "Empate", "Visita"], className }: OutcomeBarProps) {
  const segments = [
    { key: "home", value: home, label: labels[0], color: OUTCOME_COLORS.home },
    { key: "draw", value: draw, label: labels[1], color: OUTCOME_COLORS.draw },
    { key: "away", value: away, label: labels[2], color: OUTCOME_COLORS.away },
  ]
  return (
    <div className={cn("flex h-5 gap-0.5 overflow-hidden rounded-md", className)} role="img"
      aria-label={segments.map((s) => `${s.label} ${pct(s.value)}`).join(", ")}>
      {segments.map((s) => (
        <div
          key={s.key}
          className="flex min-w-0 items-center justify-center text-[0.65rem] font-semibold text-white first:rounded-l-md last:rounded-r-md"
          style={{ width: `${s.value * 100}%`, background: s.color }}
          title={`${s.label}: ${pct(s.value)}`}
        >
          {s.value >= 0.12 && pct(s.value)}
        </div>
      ))}
    </div>
  )
}
