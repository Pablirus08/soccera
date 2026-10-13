import { ActivityIcon, FlaskConicalIcon, SparklesIcon, TrendingUpIcon } from "lucide-react"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"

import { ComingSoon } from "@/components/coming-soon"
import { PageHeader } from "@/components/page-header"
import { StatTile } from "@/components/stat-tile"
import { TeamBadge } from "@/components/team-badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { LEAGUE } from "@/lib/api"
import { goalsByRound, shortName } from "@/lib/football"
import { useSnapshot } from "@/lib/league-data"

const roundConfig = { goals: { label: "Goles", color: "var(--chart-1)" } } satisfies ChartConfig

const attackDefenseConfig = {
  goals_for: { label: "Goles a favor", color: "var(--chart-1)" },
  goals_against: { label: "Goles en contra", color: "var(--chart-2)" },
} satisfies ChartConfig

export function AnalysisPage() {
  const { goals, matches, standings, discipline } = useSnapshot()

  const outcomes = [
    { label: "Local", pct: goals.home_win_pct, color: "var(--chart-1)" },
    { label: "Empate", pct: goals.draw_pct, color: "var(--chart-3)" },
    { label: "Visita", pct: goals.away_win_pct, color: "var(--chart-2)" },
  ]
  const attackDefense = standings.rows.map((r) => ({
    team: shortName(r.team_name),
    goals_for: r.goals_for,
    goals_against: r.goals_against,
  }))

  return (
    <div className="space-y-6">
      <PageHeader title="Análisis de la liga" description={`${LEAGUE.name} · ${LEAGUE.tournament}`} />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatTile label="Partidos jugados" value={goals.matches_played} hint={`${goals.total_goals} goles en total`} />
        <StatTile label="Goles por partido" value={goals.avg_goals_per_match.toFixed(2)} />
        <StatTile label="Ambos anotan" value={`${goals.btts_pct}%`} hint="de los partidos" />
        <StatTile label="Más de 2.5 goles" value={`${goals.over_2_5_pct}%`} hint="de los partidos" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>¿Quién gana los partidos?</CardTitle>
          <CardDescription>Distribución de resultados</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex h-8 gap-0.5 overflow-hidden rounded-md" role="img" aria-label="Distribución de resultados">
            {outcomes.map((o) => (
              <div
                key={o.label}
                className="flex items-center justify-center text-xs font-medium text-white first:rounded-l-md last:rounded-r-md"
                style={{ width: `${o.pct}%`, background: o.color }}
                title={`${o.label}: ${o.pct}%`}
              >
                {o.pct >= 10 && `${o.pct}%`}
              </div>
            ))}
          </div>
          <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
            {outcomes.map((o) => (
              <span key={o.label} className="flex items-center gap-1.5">
                <span className="size-2.5 rounded-sm" style={{ background: o.color }} />
                {o.label} <span className="font-medium text-foreground tabular-nums">{o.pct}%</span>
              </span>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Goles por jornada</CardTitle>
            <CardDescription>Total de goles anotados en cada jornada</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={roundConfig} className="aspect-auto h-64 w-full">
              <BarChart data={goalsByRound(matches)} margin={{ left: -16, right: 12, top: 8 }}>
                <CartesianGrid vertical={false} />
                <XAxis dataKey="round" tickLine={false} axisLine={false} tickMargin={8} />
                <YAxis tickLine={false} axisLine={false} allowDecimals={false} />
                <ChartTooltip cursor={{ fill: "var(--muted)", opacity: 0.5 }} content={<ChartTooltipContent />} />
                <Bar dataKey="goals" fill="var(--color-goals)" radius={[4, 4, 0, 0]} maxBarSize={28} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Ataque y defensa</CardTitle>
            <CardDescription>Goles a favor y en contra por equipo, en orden de la tabla</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer config={attackDefenseConfig} className="aspect-auto h-80 w-full">
              <BarChart data={attackDefense} layout="vertical" margin={{ left: 8, right: 12 }} barGap={2}>
                <CartesianGrid horizontal={false} />
                <XAxis type="number" tickLine={false} axisLine={false} allowDecimals={false} />
                <YAxis type="category" dataKey="team" tickLine={false} axisLine={false} width={112} />
                <ChartTooltip cursor={{ fill: "var(--muted)", opacity: 0.5 }} content={<ChartTooltipContent />} />
                <ChartLegend itemSorter={null} content={<ChartLegendContent />} />
                <Bar dataKey="goals_for" fill="var(--color-goals_for)" radius={[0, 4, 4, 0]} maxBarSize={10} />
                <Bar dataKey="goals_against" fill="var(--color-goals_against)" radius={[0, 4, 4, 0]} maxBarSize={10} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Disciplina</CardTitle>
          <CardDescription>Tarjetas por equipo</CardDescription>
        </CardHeader>
        <CardContent className="px-2">
          <Table className="tabular-nums">
            <TableHeader>
              <TableRow>
                <TableHead>Equipo</TableHead>
                <TableHead className="text-center">Amarillas</TableHead>
                <TableHead className="text-center">Rojas</TableHead>
                <TableHead className="text-center">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {discipline.map((d) => (
                <TableRow key={d.team_id}>
                  <TableCell className="font-medium">
                    <TeamBadge team={d.team_name} />
                  </TableCell>
                  <TableCell className="text-center">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="h-3.5 w-2.5 rounded-[2px] bg-[#fab219]" aria-hidden /> {d.yellow_cards}
                    </span>
                  </TableCell>
                  <TableCell className="text-center">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="h-3.5 w-2.5 rounded-[2px] bg-[#d03b3b]" aria-hidden /> {d.red_cards}
                    </span>
                  </TableCell>
                  <TableCell className="text-center font-semibold">{d.total_cards}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <section className="space-y-3">
        <h2 className="text-sm font-medium text-muted-foreground">Próximamente</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <ComingSoon icon={SparklesIcon} title="Predicciones de la jornada" description="Probabilidades por partido con el modelo Poisson" />
          <ComingSoon icon={TrendingUpIcon} title="Ranking Elo" description="Fuerza relativa de cada equipo a lo largo del torneo" />
          <ComingSoon icon={FlaskConicalIcon} title="Backtesting del modelo" description="Qué tan bien habría acertado el modelo en torneos pasados" />
          <ComingSoon icon={ActivityIcon} title="Estadísticas avanzadas" description="Posesión, tiros y xG promedio por equipo" />
        </div>
      </section>
    </div>
  )
}
