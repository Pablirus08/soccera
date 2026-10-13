import { DivergingBar, signed } from "@/components/analysis/diverging-bar"
import { TeamLogo } from "@/components/team-logo"
import type { PlayerSeasonStats } from "@/lib/types"

// Below this many expected goals the gap is mostly noise.
const MIN_XG = 1.5
const PER_SIDE = 6

type Row = PlayerSeasonStats & { goals: number; xg: number; diff: number }

function FinishingRow({ row, max }: { row: Row; max: number }) {
  return (
    <li className="grid grid-cols-[minmax(0,1fr)_minmax(5rem,40%)_2.5rem] items-center gap-3 py-1.5 text-sm">
      <div className="flex min-w-0 items-center gap-2">
        <TeamLogo team={row.team_name} size="sm" />
        <div className="min-w-0">
          <p className="truncate font-medium">{row.name}</p>
          <p className="text-xs text-muted-foreground tabular-nums">
            {row.goals} {row.goals === 1 ? "gol" : "goles"} · {row.xg.toFixed(1)} xG
          </p>
        </div>
      </div>
      <DivergingBar value={row.diff} max={max} />
      <span className="text-right text-xs font-medium tabular-nums">{signed(row.diff)}</span>
    </li>
  )
}

/** Goals minus expected goals: who finishes above or below their chances. */
export function FinishingChart({ players }: { players: PlayerSeasonStats[] }) {
  const rows: Row[] = players
    .map((p) => {
      const goals = p.totals.goals ?? 0
      const xg = p.totals.expectedGoals ?? 0
      return { ...p, goals, xg, diff: goals - xg }
    })
    .filter((r) => r.xg >= MIN_XG)
    .sort((a, b) => b.diff - a.diff)
  const max = Math.max(...rows.map((r) => Math.abs(r.diff)))
  const top = rows.filter((r) => r.diff > 0).slice(0, PER_SIDE)
  const bottom = rows.filter((r) => r.diff < 0).slice(-PER_SIDE).reverse()

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {[
        { title: "Por encima de lo esperado", rows: top },
        { title: "Por debajo de lo esperado", rows: bottom },
      ].map((group) => (
        <div key={group.title}>
          <p className="mb-1 text-xs font-medium text-muted-foreground">{group.title}</p>
          <ul className="divide-y">
            {group.rows.map((r) => (
              <FinishingRow key={r.player_id} row={r} max={max} />
            ))}
          </ul>
        </div>
      ))}
      <p className="text-xs text-muted-foreground md:col-span-2">
        Jugadores con al menos {MIN_XG} xG. Un valor positivo significa que convierte más de lo que
        la calidad de sus remates predice.
      </p>
    </div>
  )
}
