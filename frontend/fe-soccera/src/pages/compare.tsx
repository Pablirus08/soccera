import { ArrowLeftRightIcon } from "lucide-react"
import { Link, useSearchParams } from "react-router"

import { MOMENTUM_METRICS, PROFILE_METRICS } from "@/components/analysis/team-profile-card"
import type { LeagueMetric } from "@/components/analysis/metric-vs-league"
import { AsyncBlock } from "@/components/async-block"
import { OutcomeBar } from "@/components/outcome-bar"
import { PageHeader } from "@/components/page-header"
import { HeatmapPitch } from "@/components/pitch/heatmap"
import { ShotMap, ShotSummaryRow } from "@/components/pitch/shot-map"
import { TeamLogo } from "@/components/team-logo"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAsync } from "@/hooks/use-async"
import { fetchHeadToHead, fetchTeamVisuals } from "@/lib/api"
import { formatShortDate, shortName, teamSlug } from "@/lib/football"
import { useSnapshot } from "@/lib/league-data"
import type { HeadToHead, TeamStanding } from "@/lib/types"

const A_COLOR = "var(--chart-1)"
const B_COLOR = "var(--chart-2)"

type Row = { label: string; a: number; b: number; format: (v: number) => string; better?: "higher" | "lower" | "neutral" }

/** Mirrored bars: team A grows left from the center, team B right; the better value is bold. */
function MirrorRows({ rows }: { rows: Row[] }) {
  return (
    <ul className="space-y-2">
      {rows.map((r) => {
        const max = Math.max(Math.abs(r.a), Math.abs(r.b)) || 1
        const better = r.better ?? "higher"
        const aWins = better !== "neutral" && r.a !== r.b && (better === "higher" ? r.a > r.b : r.a < r.b)
        const bWins = better !== "neutral" && r.a !== r.b && !aWins
        return (
          <li key={r.label} className="grid grid-cols-[3.5rem_1fr_minmax(7rem,auto)_1fr_3.5rem] items-center gap-2 text-sm">
            <span className={`text-right tabular-nums ${aWins ? "font-semibold" : "text-muted-foreground"}`}>{r.format(r.a)}</span>
            <div className="flex h-2 justify-end rounded-full bg-muted">
              <div className="rounded-full" style={{ width: `${(Math.abs(r.a) / max) * 100}%`, background: A_COLOR }} />
            </div>
            <span className="text-center text-xs text-muted-foreground">{r.label}</span>
            <div className="flex h-2 rounded-full bg-muted">
              <div className="rounded-full" style={{ width: `${(Math.abs(r.b) / max) * 100}%`, background: B_COLOR }} />
            </div>
            <span className={`tabular-nums ${bWins ? "font-semibold" : "text-muted-foreground"}`}>{r.format(r.b)}</span>
          </li>
        )
      })}
    </ul>
  )
}

function metricRows<T>(metrics: LeagueMetric<T>[], a: T | undefined, b: T | undefined): Row[] {
  if (!a || !b) return []
  return metrics.map((m) => ({ label: m.label, a: m.value(a), b: m.value(b), format: m.format, better: m.better }))
}

function TeamPicker({ value, teams, onChange, exclude }: { value: string; teams: TeamStanding[]; onChange: (slug: string) => void; exclude?: string }) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-full sm:w-56">
        <SelectValue placeholder="Elegir equipo" />
      </SelectTrigger>
      <SelectContent>
        {teams
          .filter((t) => teamSlug(t.team_name) !== exclude)
          .map((t) => (
            <SelectItem key={t.team_id} value={teamSlug(t.team_name)}>
              <TeamLogo team={t.team_name} size="sm" /> {shortName(t.team_name)}
            </SelectItem>
          ))}
      </SelectContent>
    </Select>
  )
}

function HeadToHeadCard({ h, a, b }: { h: HeadToHead; a: string; b: string }) {
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Historial de enfrentamientos</CardTitle>
          <CardDescription>
            {h.played} partidos desde 2022 · goles {h.a_goals}–{h.b_goals}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {h.played > 0 && (
            <OutcomeBar
              home={h.a_wins / h.played}
              draw={h.draws / h.played}
              away={h.b_wins / h.played}
              labels={[`Gana ${shortName(a)}`, "Empate", `Gana ${shortName(b)}`]}
              className="h-7"
            />
          )}
          <p className="text-center text-xs text-muted-foreground tabular-nums">
            {shortName(a)} {h.a_wins} · Empates {h.draws} · {shortName(b)} {h.b_wins}
          </p>
          <ul className="divide-y text-sm">
            {h.matches.slice(0, 8).map((m) => (
              <li key={m.source_id}>
                <Link to={`/partidos/${m.source_id}`} className="-mx-2 grid grid-cols-[4.5rem_1fr_auto_1fr] items-center gap-2 rounded-md px-2 py-1.5 hover:bg-muted/60">
                  <span className="text-xs text-muted-foreground">
                    {formatShortDate(m.match_date)}
                    <span className="block text-[0.65rem]">{m.tournament}</span>
                  </span>
                  <span className="truncate text-right">{shortName(m.home_team)}</span>
                  <span className="rounded bg-muted px-1.5 font-medium tabular-nums">
                    {m.home_score}-{m.away_score}
                  </span>
                  <span className="truncate">{shortName(m.away_team)}</span>
                </Link>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Si se enfrentaran hoy</CardTitle>
          <CardDescription>Probabilidades del modelo según quién juegue de local</CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          {[h.a_home, h.b_home].map((p) => (
            <div key={p.home_team} className="space-y-1.5">
              <p className="text-sm">
                <span className="font-medium">{shortName(p.home_team)}</span> (local) vs {shortName(p.away_team)}
              </p>
              <OutcomeBar home={p.home_win} draw={p.draw} away={p.away_win} labels={[shortName(p.home_team), "Empate", shortName(p.away_team)]} />
              <p className="text-xs text-muted-foreground tabular-nums">
                Goles esperados {p.expected_home_goals.toFixed(1)}–{p.expected_away_goals.toFixed(1)}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

export function ComparePage() {
  const { standings, profiles, momentum, upcoming } = useSnapshot()
  const [params, setParams] = useSearchParams()
  const teams = standings.rows
  const bySlug = (slug: string | null) => teams.find((t) => teamSlug(t.team_name) === slug)

  const a = bySlug(params.get("a")) ?? teams[0]
  // Default rival: A's next opponent, else the next team in the table.
  const nextRival = upcoming.find((m) => m.home_team === a.team_name || m.away_team === a.team_name)
  const defaultB = nextRival ? (nextRival.home_team === a.team_name ? nextRival.away_team : nextRival.home_team) : undefined
  const b = bySlug(params.get("b")) ?? teams.find((t) => t.team_name === defaultB) ?? teams.find((t) => t !== a)!
  const set = (key: "a" | "b", slug: string) =>
    setParams({ a: teamSlug(a.team_name), b: teamSlug(b.team_name), [key]: slug }, { replace: true })

  const pair = `${a.team_id}-${b.team_id}`
  const h2h = useAsync(`h2h-${pair}`, () => fetchHeadToHead(a.team_id, b.team_id))
  const visA = useAsync(`team-${a.team_id}`, () => fetchTeamVisuals(a.team_id))
  const visB = useAsync(`team-${b.team_id}`, () => fetchTeamVisuals(b.team_id))

  const pos = (t: TeamStanding) => teams.indexOf(t) + 1
  const tableRows: Row[] = [
    { label: "Posición", a: pos(a), b: pos(b), format: (v) => `${v}.º`, better: "lower" },
    { label: "Puntos", a: a.points, b: b.points, format: String },
    { label: "Goles a favor", a: a.goals_for, b: b.goals_for, format: String },
    { label: "Goles en contra", a: a.goals_against, b: b.goals_against, format: String, better: "lower" },
  ]
  const profileA = profiles.find((p) => p.team_id === a.team_id)
  const profileB = profiles.find((p) => p.team_id === b.team_id)
  const momA = momentum.find((t) => t.team_id === a.team_id)
  const momB = momentum.find((t) => t.team_id === b.team_id)

  return (
    <div className="space-y-6">
      <PageHeader title="Comparar equipos" description="Cara a cara, temporada actual e historial" />

      <div className="flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
        <TeamPicker value={teamSlug(a.team_name)} teams={teams} onChange={(s) => set("a", s)} exclude={teamSlug(b.team_name)} />
        <Button
          variant="ghost"
          size="icon"
          aria-label="Intercambiar equipos"
          onClick={() => setParams({ a: teamSlug(b.team_name), b: teamSlug(a.team_name) }, { replace: true })}
        >
          <ArrowLeftRightIcon />
        </Button>
        <TeamPicker value={teamSlug(b.team_name)} teams={teams} onChange={(s) => set("b", s)} exclude={teamSlug(a.team_name)} />
      </div>

      <AsyncBlock {...h2h} skeletonClassName="h-72">
        {(h) => <HeadToHeadCard h={h} a={a.team_name} b={b.team_name} />}
      </AsyncBlock>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between gap-2">
            <span className="flex items-center gap-2"><TeamLogo team={a.team_name} size="sm" /> {shortName(a.team_name)}</span>
            <span className="text-sm font-normal text-muted-foreground">Temporada</span>
            <span className="flex items-center gap-2">{shortName(b.team_name)} <TeamLogo team={b.team_name} size="sm" /></span>
          </CardTitle>
          <CardDescription className="text-center">En negrita, el mejor en cada métrica</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <MirrorRows rows={tableRows} />
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Calidad de juego</p>
            <MirrorRows rows={metricRows(PROFILE_METRICS, profileA, profileB)} />
          </div>
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Momentum</p>
            <MirrorRows rows={metricRows(MOMENTUM_METRICS, momA, momB)} />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {[
          { team: a, vis: visA, color: A_COLOR },
          { team: b, vis: visB, color: B_COLOR },
        ].map(({ team, vis, color }) => (
          <Card key={team.team_id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TeamLogo team={team.team_name} size="sm" /> {shortName(team.team_name)}
              </CardTitle>
              <CardDescription>Dónde tiene la pelota y desde dónde remata</CardDescription>
            </CardHeader>
            <CardContent>
              <AsyncBlock {...vis} skeletonClassName="h-[36rem]">
                {(v) => (
                  <div className="space-y-5">
                    <HeatmapPitch heatmap={v.heatmap} />
                    <ShotSummaryRow summary={v.summary_for} />
                    <ShotMap shots={v.shots_for} color={color} className="mx-auto max-w-sm" />
                  </div>
                )}
              </AsyncBlock>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
