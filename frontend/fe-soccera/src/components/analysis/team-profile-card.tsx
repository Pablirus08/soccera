import { MetricVsLeague, type LeagueMetric } from "@/components/analysis/metric-vs-league"
import type { TeamMomentum, TeamProfile } from "@/lib/types"

const pct = (v: number) => `${Math.round(v * 100)}%`

export const PROFILE_METRICS: LeagueMetric<TeamProfile>[] = [
  { label: "xG a favor / partido", value: (p) => p.per_match.xg_for, format: (v) => v.toFixed(2) },
  { label: "xG en contra / partido", value: (p) => p.per_match.xg_against, format: (v) => v.toFixed(2), better: "lower" },
  { label: "Tiros / partido", value: (p) => p.per_match.shots_for, format: (v) => v.toFixed(1) },
  { label: "Tiros recibidos / partido", value: (p) => p.per_match.shots_against, format: (v) => v.toFixed(1), better: "lower" },
  { label: "Calidad por tiro (xG)", value: (p) => p.per_match.xg_per_shot, format: (v) => v.toFixed(3) },
  { label: "Posesión", value: (p) => p.possession, format: (v) => `${v.toFixed(0)}%` },
]

export const MOMENTUM_METRICS: LeagueMetric<TeamMomentum>[] = [
  { label: "Tiempo con momentum", value: (t) => t.share, format: pct, hint: "Parte del partido en que la presión va a su favor" },
  { label: "Rachas de dominio / partido", value: (t) => t.spells_per_match, format: (v) => v.toFixed(1) },
  { label: "Duración media de racha", value: (t) => t.avg_spell_minutes, format: (v) => `${v.toFixed(1)}′` },
  { label: "Rachas que terminan en gol", value: (t) => t.spell_conversion, format: pct, hint: "Anota durante la racha o en los 2 minutos siguientes" },
  { label: "xG generado por racha", value: (t) => t.xg_per_spell, format: (v) => v.toFixed(2) },
  { label: "Goles propios en sus rachas", value: (t) => t.goals_in_spells_pct, format: pct, better: "neutral", hint: "Qué parte de sus goles llega con momentum (el resto, a contracorriente)" },
  { label: "Rachas del rival / partido", value: (t) => t.rival_spells_per_match, format: (v) => v.toFixed(1), better: "lower" },
  { label: "Rachas del rival con gol", value: (t) => t.rival_spell_conversion, format: pct, better: "lower", hint: "Cuántas veces el rival aprovecha su momentum" },
  { label: "Goles recibidos en rachas rivales", value: (t) => t.goals_against_in_rival_spells_pct, format: pct, better: "neutral" },
]

export function TeamProfileCard({ team, profiles }: { team: TeamProfile; profiles: TeamProfile[] }) {
  return (
    <div className="space-y-3">
      <MetricVsLeague item={team} all={profiles} metrics={PROFILE_METRICS} />
      <p className="text-xs text-muted-foreground">
        Porcentaje mejor (+) o peor (−) que el promedio de la liga. Puntos reales {team.points} vs.{" "}
        {team.expected_points.toFixed(1)} esperados según sus ocasiones.
      </p>
    </div>
  )
}

export function TeamMomentumCard({ team, all }: { team: TeamMomentum; all: TeamMomentum[] }) {
  return (
    <div className="space-y-3">
      <MetricVsLeague item={team} all={all} metrics={MOMENTUM_METRICS} />
      <p className="text-xs text-muted-foreground">
        Racha de dominio: 4+ minutos seguidos con presión clara a su favor. En {team.matches} partidos
        con datos de momentum.
      </p>
    </div>
  )
}
