import { FormPills } from "@/components/form-pills"
import { TeamBadge } from "@/components/team-badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { recentForm } from "@/lib/football"
import type { Match, TeamStanding } from "@/lib/types"
import { cn } from "@/lib/utils"

// Top 4 advance to the semifinals in the Apertura.
const QUALIFY_SPOTS = 4

type StandingsTableProps = {
  rows: TeamStanding[]
  matches: Match[]
  highlightTeam?: string
}

export function StandingsTable({ rows, matches, highlightTeam }: StandingsTableProps) {
  return (
    <div className="space-y-2">
      <Table className="tabular-nums">
        <TableHeader>
          <TableRow>
            <TableHead className="w-8 text-center">#</TableHead>
            <TableHead>Equipo</TableHead>
            <TableHead className="text-center" title="Partidos jugados">PJ</TableHead>
            <TableHead className="hidden text-center sm:table-cell" title="Ganados">G</TableHead>
            <TableHead className="hidden text-center sm:table-cell" title="Empatados">E</TableHead>
            <TableHead className="hidden text-center sm:table-cell" title="Perdidos">P</TableHead>
            <TableHead className="hidden text-center md:table-cell" title="Goles a favor">GF</TableHead>
            <TableHead className="hidden text-center md:table-cell" title="Goles en contra">GC</TableHead>
            <TableHead className="text-center" title="Diferencia de goles">DG</TableHead>
            <TableHead className="text-center font-semibold">Pts</TableHead>
            <TableHead className="hidden lg:table-cell">Últimos 5</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, i) => (
            <TableRow
              key={row.team_id}
              data-state={row.team_name === highlightTeam ? "selected" : undefined}
            >
              <TableCell className="text-center">
                <span
                  className={cn(
                    "inline-flex size-6 items-center justify-center rounded-md text-xs font-medium",
                    i < QUALIFY_SPOTS ? "bg-primary text-primary-foreground" : "text-muted-foreground",
                  )}
                >
                  {i + 1}
                </span>
              </TableCell>
              <TableCell className="max-w-48 font-medium">
                <TeamBadge team={row.team_name} />
              </TableCell>
              <TableCell className="text-center">{row.played}</TableCell>
              <TableCell className="hidden text-center sm:table-cell">{row.won}</TableCell>
              <TableCell className="hidden text-center sm:table-cell">{row.drawn}</TableCell>
              <TableCell className="hidden text-center sm:table-cell">{row.lost}</TableCell>
              <TableCell className="hidden text-center md:table-cell">{row.goals_for}</TableCell>
              <TableCell className="hidden text-center md:table-cell">{row.goals_against}</TableCell>
              <TableCell className="text-center text-muted-foreground">
                {row.goal_diff > 0 ? `+${row.goal_diff}` : row.goal_diff}
              </TableCell>
              <TableCell className="text-center font-semibold">{row.points}</TableCell>
              <TableCell className="hidden lg:table-cell">
                <FormPills form={recentForm(row.team_name, matches)} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <p className="flex items-center gap-2 px-2 text-xs text-muted-foreground">
        <span className="inline-block size-3 rounded-sm bg-primary" /> Puestos de semifinal
      </p>
    </div>
  )
}
