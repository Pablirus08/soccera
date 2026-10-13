import { TeamBadge } from "@/components/team-badge"
import { formatMatchDay, formatMatchTime } from "@/lib/football"
import type { Match } from "@/lib/types"

/** Fixtures grouped by day; home team on top, away below, kickoff on the right. */
export function UpcomingMatches({ matches }: { matches: Match[] }) {
  if (matches.length === 0) {
    return <p className="text-sm text-muted-foreground">No hay partidos programados.</p>
  }

  const byDay = new Map<string, Match[]>()
  for (const m of [...matches].sort((a, b) => a.match_date.localeCompare(b.match_date))) {
    const day = formatMatchDay(m.match_date)
    byDay.set(day, [...(byDay.get(day) ?? []), m])
  }

  return (
    <div className="space-y-4">
      {[...byDay.entries()].map(([day, dayMatches]) => (
        <div key={day} className="space-y-1.5">
          <p className="text-xs font-medium text-muted-foreground first-letter:uppercase">{day}</p>
          <ul className="divide-y rounded-lg border">
            {dayMatches.map((m) => (
              <li key={m.source_id} className="flex items-center gap-3 px-3 py-2.5 text-sm">
                <div className="min-w-0 flex-1 space-y-1.5">
                  <TeamBadge team={m.home_team} short />
                  <TeamBadge team={m.away_team} short />
                </div>
                <span className="rounded-md bg-muted px-2 py-1 text-xs font-medium tabular-nums">
                  {formatMatchTime(m.match_date)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  )
}
