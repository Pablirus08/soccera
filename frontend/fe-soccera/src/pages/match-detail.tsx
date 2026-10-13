import { ArrowLeftIcon } from "lucide-react"
import { Link, useNavigate, useParams } from "react-router"

import { AsyncBlock } from "@/components/async-block"
import { HeatmapPitch } from "@/components/pitch/heatmap"
import { MomentumChart } from "@/components/pitch/momentum-chart"
import { ShotMap, ShotSummaryRow, summarizeShots } from "@/components/pitch/shot-map"
import { TeamLogo } from "@/components/team-logo"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAsync } from "@/hooks/use-async"
import { fetchMatchVisuals } from "@/lib/api"
import { formatDateTime, shortName, teamSlug } from "@/lib/football"
import type { MatchVisuals, SideMomentum } from "@/lib/types"

const pct = (v: number) => `${Math.round(v * 100)}%`

function Scoreboard({ m }: { m: MatchVisuals }) {
  const side = (team: string, align: "start" | "end") => (
    <Link
      to={`/equipos/${teamSlug(team)}`}
      className={`flex min-w-0 flex-1 flex-col items-center gap-2 text-center hover:underline sm:flex-row ${align === "end" ? "sm:flex-row-reverse sm:text-right" : "sm:text-left"}`}
    >
      <TeamLogo team={team} className="size-14" />
      <span className="truncate text-lg font-semibold">{shortName(team)}</span>
    </Link>
  )
  return (
    <div className="flex items-center gap-4">
      {side(m.home_team, "start")}
      <div className="shrink-0 text-center">
        <p className="text-4xl font-semibold tabular-nums">
          {m.home_score ?? "–"} <span className="text-muted-foreground">-</span> {m.away_score ?? "–"}
        </p>
        <p className="text-xs text-muted-foreground tabular-nums">
          xG {m.xg_home.toFixed(2)} – {m.xg_away.toFixed(2)}
        </p>
      </div>
      {side(m.away_team, "end")}
    </div>
  )
}

function SideSummary({ side, color }: { side: SideMomentum; color: string }) {
  return (
    <div className="space-y-2 rounded-lg border p-3">
      <p className="flex items-center gap-2 text-sm font-medium">
        <span className="size-2.5 rounded-sm" style={{ background: color }} /> {shortName(side.team_name)}
      </p>
      <dl className="grid grid-cols-2 gap-2 text-xs tabular-nums sm:grid-cols-4">
        <div>
          <dt className="text-muted-foreground">Tiempo con momentum</dt>
          <dd className="text-sm font-semibold">{pct(side.share)}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Rachas de dominio</dt>
          <dd className="text-sm font-semibold">{side.spells.length}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Rachas con gol</dt>
          <dd className="text-sm font-semibold">
            {side.spells_converted}/{side.spells.length}
          </dd>
        </div>
        <div>
          <dt className="text-muted-foreground">xG en sus rachas</dt>
          <dd className="text-sm font-semibold">{side.xg_in_spells.toFixed(2)}</dd>
        </div>
      </dl>
    </div>
  )
}

function MatchContent({ m }: { m: MatchVisuals }) {
  const homeShots = m.shots.filter((s) => s.team_name === m.home_team)
  const awayShots = m.shots.filter((s) => s.team_name === m.away_team)
  const hasVisuals = m.momentum.length > 0 || m.shots.length > 0

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="space-y-4">
          <p className="text-center text-xs text-muted-foreground">
            {m.round ? `Jornada ${m.round} · ` : ""}
            {formatDateTime(m.match_date)}
          </p>
          <Scoreboard m={m} />
          {m.goals.length > 0 && (
            <ul className="grid grid-cols-2 gap-x-6 text-xs text-muted-foreground">
              {[m.home_team, m.away_team].map((team, col) => (
                <li key={team} className={col ? "text-right" : ""}>
                  {m.goals
                    .filter((g) => g.team_name === team)
                    .map((g, i) => (
                      <p key={i}>
                        {g.player_name ?? "Gol"} {g.label}
                      </p>
                    ))}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      {!hasVisuals && (
        <p className="text-sm text-muted-foreground">
          No hay datos de momentum, tiros ni mapas de calor para este partido.
        </p>
      )}

      {m.momentum.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Momentum del partido</CardTitle>
            <CardDescription>
              Presión ofensiva minuto a minuto. Las bandas sombreadas son rachas de dominio
              sostenido (4+ minutos).
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <MomentumChart match={m} />
            <div className="grid gap-3 md:grid-cols-2">
              {m.home_momentum && <SideSummary side={m.home_momentum} color="var(--chart-1)" />}
              {m.away_momentum && <SideSummary side={m.away_momentum} color="var(--chart-2)" />}
            </div>
          </CardContent>
        </Card>
      )}

      {m.shots.length > 0 && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {[
            { team: m.home_team, shots: homeShots, color: "var(--chart-1)" },
            { team: m.away_team, shots: awayShots, color: "var(--chart-2)" },
          ].map(({ team, shots, color }) => (
            <Card key={team}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TeamLogo team={team} size="sm" /> Tiros de {shortName(team)}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <ShotSummaryRow summary={summarizeShots(shots)} />
                <ShotMap shots={shots} color={color} className="mx-auto max-w-md" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {(m.home_heatmap || m.away_heatmap) && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {[
            { team: m.home_team, heatmap: m.home_heatmap },
            { team: m.away_team, heatmap: m.away_heatmap },
          ].map(({ team, heatmap }) =>
            heatmap ? (
              <Card key={team}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TeamLogo team={team} size="sm" /> Dónde tuvo la pelota {shortName(team)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <HeatmapPitch heatmap={heatmap} />
                </CardContent>
              </Card>
            ) : null,
          )}
        </div>
      )}
    </div>
  )
}

export function MatchDetailPage() {
  const { sourceId } = useParams()
  const navigate = useNavigate()
  const state = useAsync(sourceId ?? null, () => fetchMatchVisuals(sourceId!))

  return (
    <div className="space-y-4">
      <Button variant="ghost" size="sm" className="-ml-2" onClick={() => navigate(-1)}>
        <ArrowLeftIcon data-icon="inline-start" /> Volver
      </Button>
      <AsyncBlock {...state} skeletonClassName="h-96">
        {(m) => <MatchContent m={m} />}
      </AsyncBlock>
    </div>
  )
}
