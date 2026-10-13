import { useSearchParams } from "react-router"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"

import { FinishingChart } from "@/components/analysis/finishing-chart"
import { MomentumTable } from "@/components/analysis/momentum-table"
import { PlayerLeaderboard, per90 } from "@/components/analysis/player-leaderboard"
import { PredictionCard } from "@/components/analysis/prediction-card"
import { TeamRatings } from "@/components/analysis/team-ratings"
import { XgScatter } from "@/components/analysis/xg-scatter"
import { XptsTable } from "@/components/analysis/xpts-table"
import { OUTCOME_COLORS, OutcomeBar } from "@/components/outcome-bar"
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LEAGUE } from "@/lib/api"
import { goalsByRound, shortName } from "@/lib/football"
import { useSnapshot } from "@/lib/league-data"

const roundConfig = { goals: { label: "Goles", color: "var(--chart-1)" } } satisfies ChartConfig

const attackDefenseConfig = {
  goals_for: { label: "Goles a favor", color: "var(--chart-1)" },
  goals_against: { label: "Goles en contra", color: "var(--chart-2)" },
} satisfies ChartConfig

// Per-90 leaderboards only count regulars, so a 20-minute cameo can't top them.
const MIN_MINUTES_PER90 = 450

const TABS = [
  { value: "liga", label: "Liga" },
  { value: "equipos", label: "Equipos" },
  { value: "jugadores", label: "Jugadores" },
  { value: "predicciones", label: "Predicciones" },
]

function Section({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}

function LeagueTab() {
  const { goals, matches, discipline } = useSnapshot()
  const outcomes = [
    { label: "Local", pct: goals.home_win_pct, color: OUTCOME_COLORS.home },
    { label: "Empate", pct: goals.draw_pct, color: OUTCOME_COLORS.draw },
    { label: "Visita", pct: goals.away_win_pct, color: OUTCOME_COLORS.away },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatTile label="Partidos jugados" value={goals.matches_played} hint={`${goals.total_goals} goles en total`} />
        <StatTile label="Goles por partido" value={goals.avg_goals_per_match.toFixed(2)} />
        <StatTile label="Ambos anotan" value={`${goals.btts_pct}%`} hint="de los partidos" />
        <StatTile label="Más de 2.5 goles" value={`${goals.over_2_5_pct}%`} hint="de los partidos" />
      </div>

      <Section title="¿Quién gana los partidos?" description="Distribución de resultados">
        <div className="space-y-3">
          <OutcomeBar
            home={goals.home_win_pct / 100}
            draw={goals.draw_pct / 100}
            away={goals.away_win_pct / 100}
            className="h-8"
          />
          <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
            {outcomes.map((o) => (
              <span key={o.label} className="flex items-center gap-1.5">
                <span className="size-2.5 rounded-sm" style={{ background: o.color }} />
                {o.label} <span className="font-medium text-foreground tabular-nums">{o.pct}%</span>
              </span>
            ))}
          </div>
        </div>
      </Section>

      <Section title="Goles por jornada" description="Total de goles anotados en cada jornada">
        <ChartContainer config={roundConfig} className="aspect-auto h-64 w-full">
          <BarChart data={goalsByRound(matches)} margin={{ left: -16, right: 12, top: 8 }}>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="round" tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} allowDecimals={false} />
            <ChartTooltip cursor={{ fill: "var(--muted)", opacity: 0.5 }} content={<ChartTooltipContent />} />
            <Bar dataKey="goals" fill="var(--color-goals)" radius={[4, 4, 0, 0]} maxBarSize={28} />
          </BarChart>
        </ChartContainer>
      </Section>

      <Section title="Disciplina" description="Tarjetas por equipo">
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
      </Section>
    </div>
  )
}

function TeamsTab() {
  const { profiles, standings, momentum } = useSnapshot()
  const attackDefense = standings.rows.map((r) => ({
    team: shortName(r.team_name),
    goals_for: r.goals_for,
    goals_against: r.goals_against,
  }))

  return (
    <div className="space-y-6">
      <Section
        title="Calidad de juego (xG)"
        description="Goles esperados creados vs. concedidos por partido. Las líneas punteadas son el promedio de la liga."
      >
        <XgScatter profiles={profiles} />
      </Section>

      <Section
        title="Puntos vs. puntos esperados"
        description="xPts: puntos que habría sumado cada equipo según la calidad de las ocasiones de cada partido. Una diferencia grande suele corregirse con el tiempo."
      >
        <XptsTable profiles={profiles} />
      </Section>

      <Section
        title="Momentum"
        description="Cuánto domina cada equipo sus partidos y cuántas de esas rachas (4+ minutos de presión) convierte en gol, frente a cuántas aprovechan sus rivales"
      >
        <MomentumTable teams={momentum} />
      </Section>

      <Section title="Ataque y defensa" description="Goles reales a favor y en contra, en orden de la tabla">
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
      </Section>
    </div>
  )
}

function PlayersTab() {
  const { playerSeason } = useSnapshot()
  const t = (key: string) => (p: (typeof playerSeason)[number]) => p.totals[key] ?? 0

  return (
    <div className="space-y-6">
      <Section title="Definición: goles vs. xG" description="Quién convierte más (o menos) de lo que sus remates merecen">
        <FinishingChart players={playerSeason} />
      </Section>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <Section title="Goleadores" description="Goles, goles esperados y tiros al arco">
          <PlayerLeaderboard
            players={playerSeason}
            columns={[
              { label: "G", title: "Goles", value: t("goals") },
              { label: "xG", title: "Goles esperados", value: t("expectedGoals"), digits: 1 },
              { label: "Tiros", title: "Tiros totales", value: t("totalShots") },
              { label: "Al arco", title: "Tiros al arco", value: t("onTargetScoringAttempt") },
            ]}
          />
        </Section>

        <Section
          title="Creadores de juego"
          description={`Asistencias esperadas por 90 minutos (mín. ${MIN_MINUTES_PER90}')`}
        >
          <PlayerLeaderboard
            players={playerSeason}
            minMinutes={MIN_MINUTES_PER90}
            columns={[
              { label: "xA/90", title: "Asistencias esperadas por 90'", value: (p) => per90(p.totals.expectedAssists ?? 0, p.minutes), digits: 2 },
              { label: "PC/90", title: "Pases clave por 90'", value: (p) => per90(p.totals.keyPass ?? 0, p.minutes), digits: 1 },
              { label: "A", title: "Asistencias", value: t("goalAssist") },
            ]}
          />
        </Section>

        <Section title="Muro defensivo" description={`Recuperaciones defensivas por 90 minutos (mín. ${MIN_MINUTES_PER90}')`}>
          <PlayerLeaderboard
            players={playerSeason.filter((p) => p.position !== "Goalkeeper")}
            minMinutes={MIN_MINUTES_PER90}
            columns={[
              {
                label: "Def/90",
                title: "Entradas ganadas + intercepciones + despejes por 90'",
                value: (p) =>
                  per90((p.totals.wonTackle ?? 0) + (p.totals.interceptionWon ?? 0) + (p.totals.totalClearance ?? 0), p.minutes),
                digits: 1,
              },
              { label: "Duelos/90", title: "Duelos ganados por 90'", value: (p) => per90(p.totals.duelWon ?? 0, p.minutes), digits: 1 },
            ]}
          />
        </Section>

        <Section title="Porteros" description="Atajadas y vallas invictas">
          <PlayerLeaderboard
            players={playerSeason.filter((p) => p.position === "Goalkeeper")}
            columns={[
              { label: "Atajadas", value: t("saves") },
              { label: "Invictas", title: "Vallas invictas (60'+ sin recibir gol)", value: (p) => p.clean_sheets },
              { label: "Nivel", title: "Nivel ajustado", value: (p) => p.adjusted_rating ?? 0, digits: 2 },
            ]}
          />
        </Section>
      </div>
    </div>
  )
}

function PredictionsTab() {
  const { predictions } = useSnapshot()
  const round = predictions.matches[0]?.round

  return (
    <div className="space-y-6">
      <Section
        title={round ? `Jornada ${round}` : "Próxima jornada"}
        description="Probabilidades de un modelo Poisson: ataque y defensa de cada equipo más la ventaja de local"
      >
        {predictions.matches.length ? (
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            {predictions.matches.map((p) => (
              <PredictionCard key={p.source_id} prediction={p} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No hay partidos programados.</p>
        )}
      </Section>

      <Section
        title="Fuerza de los equipos"
        description={`Estimada con ${predictions.trained_on.toLocaleString("es-CR")} partidos desde 2022 · jugar de local multiplica los goles esperados por ×${predictions.home_advantage.toFixed(2)}`}
      >
        <TeamRatings ratings={predictions.ratings} />
      </Section>

      <p className="text-xs text-muted-foreground">
        En el backtest (predecir cada torneo solo con partidos anteriores) el modelo acierta el
        resultado el 51% de las veces, contra 45% de una referencia que solo usa la frecuencia
        histórica de local/empate/visita. Úsalo como guía, no como certeza.
      </p>
    </div>
  )
}

export function AnalysisPage() {
  const [params, setParams] = useSearchParams()
  const tab = TABS.some((t) => t.value === params.get("tab")) ? params.get("tab")! : "liga"

  return (
    <div className="space-y-6">
      <PageHeader title="Análisis" description={`${LEAGUE.name} · ${LEAGUE.tournament}`} />
      <Tabs value={tab} onValueChange={(value) => setParams({ tab: value }, { replace: true })}>
        <TabsList className="w-full sm:w-fit">
          {TABS.map((t) => (
            <TabsTrigger key={t.value} value={t.value}>
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>
        <TabsContent value="liga" className="mt-4">
          <LeagueTab />
        </TabsContent>
        <TabsContent value="equipos" className="mt-4">
          <TeamsTab />
        </TabsContent>
        <TabsContent value="jugadores" className="mt-4">
          <PlayersTab />
        </TabsContent>
        <TabsContent value="predicciones" className="mt-4">
          <PredictionsTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
