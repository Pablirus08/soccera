import { CartesianGrid, ReferenceLine, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts"

import { ChartContainer, type ChartConfig } from "@/components/ui/chart"
import { shortName, teamInitials, teamLogoUrl } from "@/lib/football"
import type { TeamProfile } from "@/lib/types"

const config = { team: { label: "Equipo", color: "var(--chart-1)" } } satisfies ChartConfig

type Point = { team: string; x: number; y: number; goalsFor: number; goalsAgainst: number }

const LOGO = 28

/** Axis bounds padded and snapped to a 0.2 grid, with evenly spaced ticks. */
function niceAxis(values: number[], step = 0.2) {
  const min = Math.floor((Math.min(...values) - step / 2) / step) * step
  const max = Math.ceil((Math.max(...values) + step / 2) / step) * step
  const ticks = []
  for (let v = min; v <= max + 1e-9; v += step) ticks.push(+v.toFixed(1))
  return { min: +min.toFixed(1), max: +max.toFixed(1), ticks }
}

/** Each team drawn as its crest (initials disc if it has none). */
function CrestDot({ cx, cy, payload }: { cx?: number; cy?: number; payload?: Point }) {
  if (cx === undefined || cy === undefined || !payload) return null
  const src = teamLogoUrl(payload.team)
  return src ? (
    <image href={src} x={cx - LOGO / 2} y={cy - LOGO / 2} width={LOGO} height={LOGO} />
  ) : (
    <g>
      <circle cx={cx} cy={cy} r={12} fill="var(--muted)" stroke="var(--border)" />
      <text x={cx} y={cy} dy="0.35em" textAnchor="middle" fontSize={9} fill="var(--foreground)">
        {teamInitials(payload.team)}
      </text>
    </g>
  )
}

function PointTooltip({ active, payload }: { active?: boolean; payload?: { payload: Point }[] }) {
  if (!active || !payload?.length) return null
  const p = payload[0].payload
  return (
    <div className="rounded-lg border bg-background px-3 py-2 text-xs shadow-md">
      <p className="mb-1 font-medium">{p.team}</p>
      <p className="tabular-nums text-muted-foreground">
        xG a favor <span className="font-medium text-foreground">{p.x.toFixed(2)}</span> · en contra{" "}
        <span className="font-medium text-foreground">{p.y.toFixed(2)}</span> por partido
      </p>
      <p className="tabular-nums text-muted-foreground">
        Goles reales {p.goalsFor}–{p.goalsAgainst}
      </p>
    </div>
  )
}

/**
 * Chance quality map: x = xG created per match, y = xG conceded per match
 * (axis reversed, so up means "concedes less"). Dashed lines mark the league
 * average, splitting the plot into four profiles.
 */
export function XgScatter({ profiles }: { profiles: TeamProfile[] }) {
  const data: Point[] = profiles.map((p) => ({
    team: p.team_name,
    x: p.per_match.xg_for,
    y: p.per_match.xg_against,
    goalsFor: p.goals_for,
    goalsAgainst: p.goals_against,
  }))
  const avg = (vals: number[]) => vals.reduce((a, b) => a + b, 0) / vals.length
  const avgX = avg(data.map((d) => d.x))
  const avgY = avg(data.map((d) => d.y))
  const xAxis = niceAxis(data.map((d) => d.x))
  const yAxis = niceAxis(data.map((d) => d.y))

  return (
    <div className="space-y-1">
      <p className="text-xs text-muted-foreground">↑ concede menos (xG en contra por partido)</p>
      <div className="relative">
        <ChartContainer config={config} className="aspect-auto h-96 w-full">
          <ScatterChart margin={{ top: 16, right: 20, bottom: 4, left: 0 }}>
            <CartesianGrid strokeDasharray="0" />
            <XAxis
              type="number"
              dataKey="x"
              domain={[xAxis.min, xAxis.max]}
              ticks={xAxis.ticks}
              tickFormatter={(v: number) => v.toFixed(1)}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              type="number"
              dataKey="y"
              reversed
              domain={[yAxis.min, yAxis.max]}
              ticks={yAxis.ticks}
              tickFormatter={(v: number) => v.toFixed(1)}
              tickLine={false}
              axisLine={false}
              width={36}
            />
            <ReferenceLine x={avgX} stroke="var(--muted-foreground)" strokeDasharray="4 4" strokeOpacity={0.6} />
            <ReferenceLine y={avgY} stroke="var(--muted-foreground)" strokeDasharray="4 4" strokeOpacity={0.6} />
            <Tooltip cursor={false} content={<PointTooltip />} />
            <Scatter
              data={data}
              shape={(props: unknown) => <CrestDot {...(props as Parameters<typeof CrestDot>[0])} />}
              isAnimationActive={false}
            />
          </ScatterChart>
        </ChartContainer>
        {/* Quadrant names, inset inside the plot area (margins + axis sizes above). */}
        <div className="pointer-events-none absolute inset-0 text-[0.7rem] font-medium text-muted-foreground/80">
          <span className="absolute top-5 right-6">Dominan</span>
          <span className="absolute top-5 left-12">Sólidos atrás</span>
          <span className="absolute right-6 bottom-10">Atacan pero conceden</span>
          <span className="absolute bottom-10 left-12">Sufren</span>
        </div>
      </div>
      <p className="text-center text-xs text-muted-foreground">xG a favor por partido →</p>
      <p className="sr-only">
        {data.map((d) => `${shortName(d.team)}: ${d.x.toFixed(2)} xG a favor, ${d.y.toFixed(2)} en contra`).join(". ")}
      </p>
    </div>
  )
}
