import { Area, AreaChart, CartesianGrid, ReferenceArea, ReferenceDot, ReferenceLine, Tooltip, XAxis, YAxis } from "recharts"

import { ChartContainer, type ChartConfig } from "@/components/ui/chart"
import { shortName } from "@/lib/football"
import type { MatchVisuals } from "@/lib/types"

type Row = { minute: number; home: number; away: number; raw: number }

function MomentumTooltip({ active, payload, home, away }: { active?: boolean; payload?: { payload: Row }[]; home: string; away: string }) {
  if (!active || !payload?.length) return null
  const r = payload[0].payload
  const side = r.raw > 0 ? home : r.raw < 0 ? away : null
  return (
    <div className="rounded-lg border bg-background px-2.5 py-1.5 text-xs shadow-md">
      <p className="font-medium tabular-nums">Minuto {r.minute}</p>
      <p className="text-muted-foreground">
        {side ? `Presiona ${shortName(side)} (${Math.abs(r.raw)})` : "Equilibrado"}
      </p>
    </div>
  )
}

/**
 * Attacking-pressure curve: home above the axis, away below. Shaded bands
 * are dominance spells; dashed lines mark goals (dot on the scorer's side).
 */
export function MomentumChart({ match }: { match: MatchVisuals }) {
  const data: Row[] = match.momentum.map(([minute, v]) => ({
    minute,
    home: Math.max(v, 0),
    away: Math.min(v, 0),
    raw: v,
  }))
  const peak = Math.max(40, ...match.momentum.map(([, v]) => Math.abs(v)))
  const config = {
    home: { label: match.home_team, color: "var(--chart-1)" },
    away: { label: match.away_team, color: "var(--chart-2)" },
  } satisfies ChartConfig

  return (
    <div className="space-y-2">
      <ChartContainer config={config} className="aspect-auto h-64 w-full">
        <AreaChart data={data} margin={{ top: 12, right: 8, bottom: 0, left: 8 }}>
          <CartesianGrid vertical={false} strokeOpacity={0.5} />
          <XAxis
            type="number"
            dataKey="minute"
            domain={[0, 91]}
            ticks={[0, 15, 30, 45, 60, 75, 90]}
            tickFormatter={(m: number) => `${m}'`}
            tickLine={false}
            axisLine={false}
          />
          <YAxis hide domain={[-peak * 1.15, peak * 1.15]} />
          {match.home_momentum?.spells.map((s) => (
            <ReferenceArea key={`h${s.start}`} x1={s.start} x2={s.end} y1={0} y2={peak * 1.15} fill="var(--chart-1)" fillOpacity={0.1} />
          ))}
          {match.away_momentum?.spells.map((s) => (
            <ReferenceArea key={`a${s.start}`} x1={s.start} x2={s.end} y1={-peak * 1.15} y2={0} fill="var(--chart-2)" fillOpacity={0.1} />
          ))}
          <ReferenceLine y={0} stroke="var(--border)" />
          <ReferenceLine x={45.5} stroke="var(--muted-foreground)" strokeOpacity={0.5} label={{ value: "Descanso", position: "insideTopRight", fontSize: 10, fill: "var(--muted-foreground)" }} />
          <Area type="monotone" dataKey="home" stroke="var(--color-home)" fill="var(--color-home)" fillOpacity={0.55} strokeWidth={1.5} isAnimationActive={false} />
          <Area type="monotone" dataKey="away" stroke="var(--color-away)" fill="var(--color-away)" fillOpacity={0.55} strokeWidth={1.5} isAnimationActive={false} />
          {match.goals.map((g, i) => {
            const isHome = g.team_name === match.home_team
            return (
              <g key={i}>
                <ReferenceLine x={g.minute} stroke="var(--foreground)" strokeOpacity={0.45} strokeDasharray="3 3" />
                <ReferenceDot
                  x={g.minute}
                  y={isHome ? peak * 1.05 : -peak * 1.05}
                  r={5}
                  fill={isHome ? "var(--chart-1)" : "var(--chart-2)"}
                  stroke="var(--background)"
                  strokeWidth={2}
                />
              </g>
            )
          })}
          <Tooltip cursor={{ stroke: "var(--muted-foreground)", strokeOpacity: 0.4 }} content={<MomentumTooltip home={match.home_team} away={match.away_team} />} />
        </AreaChart>
      </ChartContainer>
      <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
        {[
          { name: match.home_team, color: "var(--chart-1)" },
          { name: match.away_team, color: "var(--chart-2)" },
        ].map((t) => (
          <span key={t.name} className="flex items-center gap-1.5">
            <span className="size-2.5 rounded-sm" style={{ background: t.color }} />
            {shortName(t.name)}
          </span>
        ))}
        <span className="flex items-center gap-1.5">
          <span className="size-2.5 rounded-sm bg-muted-foreground/25" /> Racha de dominio
        </span>
        <span className="flex items-center gap-1.5">
          <span className="size-2.5 rounded-full bg-foreground/60" /> Gol
        </span>
      </div>
    </div>
  )
}
