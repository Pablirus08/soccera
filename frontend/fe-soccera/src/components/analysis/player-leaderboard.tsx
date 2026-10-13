import { TeamLogo } from "@/components/team-logo"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { PlayerSeasonStats } from "@/lib/types"

export type LeaderboardColumn = {
  label: string
  title?: string
  value: (p: PlayerSeasonStats) => number
  digits?: number
}

type PlayerLeaderboardProps = {
  players: PlayerSeasonStats[]
  /** First column is the sort key. */
  columns: LeaderboardColumn[]
  minMinutes?: number
  limit?: number
}

/** Ranked player table: sorted by the first column, descending. */
export function PlayerLeaderboard({ players, columns, minMinutes = 0, limit = 8 }: PlayerLeaderboardProps) {
  const [sortBy] = columns
  const rows = players
    .filter((p) => p.minutes >= minMinutes)
    .sort((a, b) => sortBy.value(b) - sortBy.value(a))
    .slice(0, limit)

  return (
    <Table className="tabular-nums">
      <TableHeader>
        <TableRow>
          <TableHead className="w-6">#</TableHead>
          <TableHead>Jugador</TableHead>
          {columns.map((c, i) => (
            <TableHead key={c.label} title={c.title} className={i === 0 ? "text-right font-semibold" : "text-right"}>
              {c.label}
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((p, i) => (
          <TableRow key={p.player_id}>
            <TableCell className="text-muted-foreground">{i + 1}</TableCell>
            <TableCell>
              <div className="flex min-w-0 items-center gap-2">
                <TeamLogo team={p.team_name} size="sm" />
                <div className="min-w-0">
                  <p className="truncate font-medium">{p.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {p.matches} PJ · {p.minutes}&#8242;
                  </p>
                </div>
              </div>
            </TableCell>
            {columns.map((c, ci) => (
              <TableCell key={c.label} className={ci === 0 ? "text-right font-semibold" : "text-right text-muted-foreground"}>
                {c.value(p).toFixed(c.digits ?? 0)}
              </TableCell>
            ))}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export const per90 = (total: number, minutes: number) => (minutes ? (total / minutes) * 90 : 0)
