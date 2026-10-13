import { TeamBadge } from "@/components/team-badge"
import type { TeamRating } from "@/lib/types"

const factor = (v: number) => `×${v.toFixed(2)}`

/** Model strength per team; bar length = overall strength (attack × defense). */
export function TeamRatings({ ratings }: { ratings: TeamRating[] }) {
  const max = Math.max(...ratings.map((r) => r.strength))
  return (
    <div className="space-y-1">
      <div className="grid grid-cols-[minmax(0,1fr)_3.5rem_3.5rem_minmax(4rem,35%)] gap-3 px-1 text-xs text-muted-foreground">
        <span>Equipo</span>
        <span className="text-right" title="Goles que anota frente a un equipo promedio">Ataque</span>
        <span className="text-right" title="Mayor = recibe menos goles que el promedio">Defensa</span>
        <span>Fuerza total</span>
      </div>
      <ul className="divide-y">
        {ratings.map((r) => (
          <li key={r.team_id} className="grid grid-cols-[minmax(0,1fr)_3.5rem_3.5rem_minmax(4rem,35%)] items-center gap-3 px-1 py-2 text-sm tabular-nums">
            <TeamBadge team={r.team_name} short className="font-medium" />
            <span className="text-right">{factor(r.attack)}</span>
            <span className="text-right">{factor(r.defense)}</span>
            <div className="flex items-center gap-2">
              <div className="h-2.5 flex-1 rounded-full bg-muted">
                <div className="h-full rounded-full bg-chart-1" style={{ width: `${(r.strength / max) * 100}%` }} />
              </div>
              <span className="w-10 text-right text-xs font-medium">{factor(r.strength)}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
