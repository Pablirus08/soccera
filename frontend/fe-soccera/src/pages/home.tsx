import { CalendarDaysIcon, ListOrderedIcon, StarIcon } from "lucide-react"

import { MockBadge } from "@/components/mock-badge"
import { PageHeader } from "@/components/page-header"
import { StandingsTable } from "@/components/standings-table"
import { TopPlayers } from "@/components/top-players"
import { UpcomingMatches } from "@/components/upcoming-matches"
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { LEAGUE } from "@/lib/api"
import { lastPlayedRound } from "@/lib/football"
import { useSnapshot } from "@/lib/league-data"

export function HomePage() {
  const { standings, matches, upcoming, players } = useSnapshot()
  const played = lastPlayedRound(matches)
  const nextRound = upcoming[0]?.round

  return (
    <div className="space-y-6">
      <PageHeader
        title={`${LEAGUE.name} · ${LEAGUE.tournament}`}
        description={`Jornada ${played} completada${nextRound ? ` · Próxima: jornada ${nextRound}` : ""}`}
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ListOrderedIcon className="size-4 text-muted-foreground" /> Tabla de posiciones
            </CardTitle>
            <CardDescription>Tras {played} jornadas</CardDescription>
          </CardHeader>
          <CardContent className="px-2">
            <StandingsTable rows={standings.rows} matches={matches} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarDaysIcon className="size-4 text-muted-foreground" /> Próxima jornada
            </CardTitle>
            <CardDescription>
              {nextRound ? `Jornada ${nextRound} · hora de Costa Rica` : "Sin partidos programados"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <UpcomingMatches matches={upcoming} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <StarIcon className="size-4 text-muted-foreground" /> Mejores jugadores
          </CardTitle>
          <CardDescription>Por posición, según calificación promedio</CardDescription>
          <CardAction>
            <MockBadge />
          </CardAction>
        </CardHeader>
        <CardContent>
          <TopPlayers players={players} />
        </CardContent>
      </Card>
    </div>
  )
}
