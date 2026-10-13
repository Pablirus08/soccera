import { DivergingBar } from "@/components/analysis/diverging-bar"

export type LeagueMetric<T> = {
  label: string
  value: (item: T) => number
  format: (v: number) => string
  /** "lower" when less is better (e.g. chances conceded); "neutral" shows no verdict. */
  better?: "higher" | "lower" | "neutral"
  hint?: string
}

/**
 * One item against the league average on each metric. Bars show how much
 * better (blue, right) or worse (red, left) than average, already flipped
 * for metrics where less is better.
 */
export function MetricVsLeague<T>({ item, all, metrics }: { item: T; all: T[]; metrics: LeagueMetric<T>[] }) {
  const rows = metrics.map((m) => {
    const avg = all.reduce((s, x) => s + m.value(x), 0) / (all.length || 1)
    const value = m.value(item)
    const rel = avg ? (value - avg) / avg : 0
    const direction = m.better ?? "higher"
    return { ...m, avg, value, direction, score: direction === "lower" ? -rel : rel }
  })
  const max = Math.max(0.25, ...rows.filter((r) => r.direction !== "neutral").map((r) => Math.abs(r.score)))

  return (
    <ul className="space-y-2.5">
      {rows.map((r) => (
        <li
          key={r.label}
          className="grid grid-cols-[minmax(0,1fr)_3.5rem_minmax(4rem,35%)_3rem] items-center gap-3 text-sm"
          title={r.hint}
        >
          <span className="truncate text-muted-foreground">{r.label}</span>
          <span className="text-right font-medium tabular-nums">{r.format(r.value)}</span>
          {r.direction === "neutral" ? (
            <span className="text-center text-xs text-muted-foreground tabular-nums">liga {r.format(r.avg)}</span>
          ) : (
            <DivergingBar value={r.score} max={max} />
          )}
          <span className="text-right text-xs tabular-nums text-muted-foreground" title={`Promedio de la liga: ${r.format(r.avg)}`}>
            {r.direction === "neutral" ? "" : `${r.score >= 0 ? "+" : "−"}${Math.abs(Math.round(r.score * 100))}%`}
          </span>
        </li>
      ))}
    </ul>
  )
}
