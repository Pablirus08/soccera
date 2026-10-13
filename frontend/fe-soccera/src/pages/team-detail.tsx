import {
  ArrowLeftIcon,
  CrosshairIcon,
  GitCompareArrowsIcon,
  MapIcon,
  SparklesIcon,
} from "lucide-react"
import { Bar, BarChart, CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts"
import { Link, useParams } from "react-router"

import { ComingSoon } from "@/components/coming-soon"
import { FormPills } from "@/components/form-pills"
import { MockBadge } from "@/components/mock-badge"
import { PageHeader } from "@/components/page-header"
import { StatTile } from "@/components/stat-tile"
import { TeamBadge } from "@/components/team-badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import {
  formatMatchDay,
  formatMatchTime,
  formatShortDate,
  goalsPerMatch,
  homeAwaySplit,
  isPlayed,
  POSITION_LABELS,
  pointsProgression,
  recentForm,
  resultFor,
  teamMatches,
  teamSlug,
} from "@/lib/football"
import { useSnapshot } from "@/lib/league-data"

const pointsConfig = { points: { label: "Puntos", color: "var(--chart-1)" } } satisfies ChartConfig

const goalsConfig = {
  favor: { label: "A favor", color: "var(--chart-1)" },
  contra: { label: "En contra", color: "var(--chart-2)" },
} satisfies ChartConfig

export function TeamDetailPage() {
  const { slug } = useParams()
  const { standings, matches, upcoming, players } = useSnapshot()

  const index = standings.rows.findIndex((r) => teamSlug(r.team_name) === slug)
  const row = standings.rows[index]

  if (!row) {
    return (
      <div className="space-y-4">
        <PageHeader title="Equipo no encontrado" />
        <Button variant="outline" asChild>
          <Link to="/equipos">
            <ArrowLeftIcon data-icon="inline-start" /> Volver a equipos
          </Link>
        </Button>
      </div>
    )
  }

  const team = row.team_name
  const played = teamMatches(team, matches).filter(isPlayed).reverse()
  const next = upcoming.find((m) => m.home_team === team || m.away_team === team)
  const split = homeAwaySplit(team, matches)
  const squad = players.filter((p) => p.team_name === team).sort((a, b) => b.rating - a.rating)
  const perMatch = (n: number) => (row.played ? (n / row.played).toFixed(2) : "–")

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <Button variant="ghost" size="sm" asChild className="-ml-2">
          <Link to="/equipos">
            <ArrowLeftIcon data-icon="inline-start" /> Equipos
          </Link>
        </Button>
        <PageHeader
          title={<TeamBadge team={team} size="lg" link={false} />}
          description={`${index + 1}.º lugar · ${row.points} puntos en ${row.played} partidos`}
        >
          <FormPills form={recentForm(team, matches)} />
        </PageHeader>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatTile label="Posición" value={`${index + 1}.º`} hint={`de ${standings.rows.length} equipos`} />
        <StatTile label="Puntos" value={row.points} hint={`${row.won}G · ${row.drawn}E · ${row.lost}P`} />
        <StatTile label="Goles a favor" value={row.goals_for} hint={`${perMatch(row.goals_for)} por partido`} />
        <StatTile label="Goles en contra" value={row.goals_against} hint={`${perMatch(row.goals_against)} por partido`} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Evolución de puntos</CardTitle>
            <CardDescription>Puntos acumulados por jornada</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={pointsConfig} className="aspect-auto h-64 w-full">
              <LineChart data={pointsProgression(team, matches)} margin={{ left: -16, right: 12, top: 8 }}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="round" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis tickLine={false} axisLine={false} allowDecimals={false} />
                <ChartTooltip cursor content={<ChartTooltipContent />} />
                <Line
                  dataKey="points"
                  type="monotone"
                  stroke="var(--color-points)"
                  strokeWidth={2}
                  dot={{ r: 4, fill: "var(--color-points)", stroke: "var(--card)", strokeWidth: 2 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Local vs. visitante</CardTitle>
            <CardDescription>Rendimiento según condición</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {([
              ["Local", split.home],
              ["Visitante", split.away],
            ] as const).map(([label, s]) => (
              <div key={label} className="space-y-1.5">
                <div className="flex items-baseline justify-between text-sm">
                  <span className="font-medium">{label}</span>
                  <span className="tabular-nums text-muted-foreground">
                    {s.points} pts en {s.played} PJ
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-chart-1"
                    style={{ width: `${s.played ? (s.points / (s.played * 3)) * 100 : 0}%` }}
                  />
                </div>
                <p className="text-xs tabular-nums text-muted-foreground">
                  {s.won}G · {s.drawn}E · {s.lost}P · goles {s.gf}-{s.ga} ·{" "}
                  {s.played ? Math.round((s.points / (s.played * 3)) * 100) : 0}% de puntos
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Goles por partido</CardTitle>
            <CardDescription>A favor y en contra en cada jornada</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={goalsConfig} className="aspect-auto h-64 w-full">
              <BarChart data={goalsPerMatch(team, matches)} margin={{ left: -16, right: 12, top: 8 }} barGap={2}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="round" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis tickLine={false} axisLine={false} allowDecimals={false} />
                <ChartTooltip
                  cursor={{ fill: "var(--muted)", opacity: 0.5 }}
                  content={
                    <ChartTooltipContent
                      labelFormatter={(label, payload) => `${label} · vs ${payload?.[0]?.payload?.rival ?? ""}`}
                    />
                  }
                />
                <ChartLegend itemSorter={null} content={<ChartLegendContent />} />
                <Bar dataKey="favor" fill="var(--color-favor)" radius={[4, 4, 0, 0]} maxBarSize={18} />
                <Bar dataKey="contra" fill="var(--color-contra)" radius={[4, 4, 0, 0]} maxBarSize={18} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Partidos</CardTitle>
            <CardDescription>Próximo y resultados recientes</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {next && (
              <div className="rounded-lg border bg-muted/40 p-3 text-sm">
                <p className="mb-1 text-xs text-muted-foreground">
                  Próximo · {formatMatchDay(next.match_date)} · {formatMatchTime(next.match_date)}
                </p>
                <p className="font-medium">
                  {next.home_team === team ? "vs " : "@ "}
                  {next.home_team === team ? next.away_team : next.home_team}
                </p>
              </div>
            )}
            <ul className="divide-y text-sm">
              {played.slice(0, 6).map((m) => {
                const r = resultFor(team, m)!
                const home = m.home_team === team
                return (
                  <li key={m.source_id} className="flex items-center gap-2 py-2">
                    <FormPills form={[r]} />
                    <span className="min-w-0 flex-1 truncate">
                      {home ? "vs " : "@ "}
                      {home ? m.away_team : m.home_team}
                    </span>
                    <span className="font-medium tabular-nums">
                      {home ? `${m.home_score}-${m.away_score}` : `${m.away_score}-${m.home_score}`}
                    </span>
                    <span className="w-12 text-right text-xs text-muted-foreground">
                      {formatShortDate(m.match_date)}
                    </span>
                  </li>
                )
              })}
            </ul>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Jugadores destacados</CardTitle>
          <CardDescription>Mejor calificación del plantel</CardDescription>
          <CardAction>
            <MockBadge />
          </CardAction>
        </CardHeader>
        <CardContent>
          {squad.length ? (
            <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {squad.map((p) => (
                <li key={p.id} className="flex items-center gap-3 rounded-lg border p-3">
                  <Avatar>
                    <AvatarFallback className="text-xs">
                      {p.name.split(" ").map((w) => w[0]).join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{p.name}</p>
                    <p className="text-xs text-muted-foreground">{POSITION_LABELS[p.position]}</p>
                  </div>
                  <Badge>{p.rating.toFixed(1)}</Badge>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">Aún no hay datos de jugadores para este equipo.</p>
          )}
        </CardContent>
      </Card>

      <section className="space-y-3">
        <h2 className="text-sm font-medium text-muted-foreground">Próximamente</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <ComingSoon icon={SparklesIcon} title="Predicción del próximo partido" description="Probabilidades 1X2 con el modelo Poisson del backend" />
          <ComingSoon icon={CrosshairIcon} title="Goles esperados (xG)" description="Calidad de las ocasiones creadas y concedidas" />
          <ComingSoon icon={MapIcon} title="Mapa de tiros" description="Dónde remata y desde dónde le rematan" />
          <ComingSoon icon={GitCompareArrowsIcon} title="Comparar con rival" description="Cara a cara estadístico antes de cada partido" />
        </div>
      </section>
    </div>
  )
}
