import { OutcomeBar } from "@/components/outcome-bar"
import { TeamBadge } from "@/components/team-badge"
import { formatMatchDay, formatMatchTime, shortName } from "@/lib/football"
import type { MatchPrediction } from "@/lib/types"

const pct = (v: number) => `${Math.round(v * 100)}%`

/** One fixture's model forecast: 1X2 bar plus expected goals and markets. */
export function PredictionCard({ prediction: p }: { prediction: MatchPrediction }) {
  return (
    <div className="space-y-3 rounded-lg border p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 space-y-1.5 text-sm font-medium">
          <TeamBadge team={p.home_team} short />
          <TeamBadge team={p.away_team} short />
        </div>
        <div className="shrink-0 text-right text-xs text-muted-foreground">
          <p className="first-letter:uppercase">{formatMatchDay(p.match_date)}</p>
          <p className="tabular-nums">{formatMatchTime(p.match_date)}</p>
        </div>
      </div>
      <OutcomeBar
        home={p.home_win}
        draw={p.draw}
        away={p.away_win}
        labels={[shortName(p.home_team), "Empate", shortName(p.away_team)]}
      />
      <dl className="grid grid-cols-4 gap-2 text-center text-xs tabular-nums">
        <div>
          <dt className="text-muted-foreground">Goles esp.</dt>
          <dd className="font-medium">
            {p.expected_home_goals.toFixed(1)}–{p.expected_away_goals.toFixed(1)}
          </dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Marcador</dt>
          <dd className="font-medium" title={`Probabilidad del marcador exacto: ${pct(p.likely_score_prob)}`}>
            {p.likely_score} <span className="text-muted-foreground">({pct(p.likely_score_prob)})</span>
          </dd>
        </div>
        <div>
          <dt className="text-muted-foreground">+2.5 goles</dt>
          <dd className="font-medium">{pct(p.over_2_5)}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Ambos anotan</dt>
          <dd className="font-medium">{pct(p.both_score)}</dd>
        </div>
      </dl>
    </div>
  )
}
