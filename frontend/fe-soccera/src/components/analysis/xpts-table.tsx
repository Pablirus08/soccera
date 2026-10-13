import { DivergingBar, signed } from "@/components/analysis/diverging-bar"
import { TeamBadge } from "@/components/team-badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { TeamProfile } from "@/lib/types"

/** Points vs. expected points (xPts), sorted from luckiest to unluckiest. */
export function XptsTable({ profiles }: { profiles: TeamProfile[] }) {
  const rows = profiles
    .map((p) => ({ ...p, diff: p.points - p.expected_points }))
    .sort((a, b) => b.diff - a.diff)
  const max = Math.max(...rows.map((r) => Math.abs(r.diff)))

  return (
    <Table className="tabular-nums">
      <TableHeader>
        <TableRow>
          <TableHead>Equipo</TableHead>
          <TableHead className="text-center" title="Partidos con estadísticas disponibles">PJ</TableHead>
          <TableHead className="text-center" title="Puntos reales">Pts</TableHead>
          <TableHead className="text-center" title="Puntos esperados según la calidad de las ocasiones (xG)">xPts</TableHead>
          <TableHead className="w-[30%] min-w-32 text-center">Diferencia</TableHead>
          <TableHead className="hidden text-center md:table-cell" title="Goles a favor vs. goles esperados">GF / xG</TableHead>
          <TableHead className="hidden text-center md:table-cell" title="Goles en contra vs. goles esperados en contra">GC / xGC</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r) => (
          <TableRow key={r.team_id}>
            <TableCell className="max-w-44 font-medium">
              <TeamBadge team={r.team_name} short />
            </TableCell>
            <TableCell className="text-center text-muted-foreground">{r.matches}</TableCell>
            <TableCell className="text-center font-semibold">{r.points}</TableCell>
            <TableCell className="text-center text-muted-foreground">{r.expected_points.toFixed(1)}</TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                <DivergingBar value={r.diff} max={max} />
                <span className="w-10 shrink-0 text-right text-xs font-medium">{signed(r.diff)}</span>
              </div>
            </TableCell>
            <TableCell className="hidden text-center md:table-cell">
              {r.goals_for} <span className="text-muted-foreground">/ {r.xg_for.toFixed(1)}</span>
            </TableCell>
            <TableCell className="hidden text-center md:table-cell">
              {r.goals_against} <span className="text-muted-foreground">/ {r.xg_against.toFixed(1)}</span>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
