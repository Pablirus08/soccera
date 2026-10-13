import { useId } from "react"

import { FullPitch, PITCH_LENGTH, PITCH_WIDTH } from "@/components/pitch/pitch"
import type { Heatmap } from "@/lib/types"

/** Share of touches per third (along the pitch) and wings vs. center (across it). */
export function heatmapZones(h: Heatmap) {
  const total = h.grid.reduce((a, b) => a + b, 0) || 1
  const third = h.cols / 3
  const wing = Math.round(h.rows * 0.3)
  const thirds = [0, 0, 0]
  let wings = 0
  h.grid.forEach((v, i) => {
    const row = Math.floor(i / h.cols)
    const col = i % h.cols
    thirds[Math.min(Math.floor(col / third), 2)] += v
    if (row < wing || row >= h.rows - wing) wings += v
  })
  return {
    own: thirds[0] / total,
    middle: thirds[1] / total,
    attack: thirds[2] / total,
    wings: wings / total,
    center: 1 - wings / total,
  }
}

const pct = (v: number) => `${Math.round(v * 100)}%`

function ZoneBar({ parts }: { parts: { label: string; value: number }[] }) {
  return (
    <div className="space-y-1">
      <div className="flex h-2 gap-0.5 overflow-hidden rounded-full">
        {parts.map((p, i) => (
          <div
            key={p.label}
            className="bg-chart-1 first:rounded-l-full last:rounded-r-full"
            style={{ width: `${p.value * 100}%`, opacity: 0.35 + i * 0.3 }}
          />
        ))}
      </div>
      <div className="flex justify-between text-[0.7rem] text-muted-foreground tabular-nums">
        {parts.map((p) => (
          <span key={p.label}>
            {p.label} <span className="font-medium text-foreground">{pct(p.value)}</span>
          </span>
        ))}
      </div>
    </div>
  )
}

/**
 * Where a team has the ball: touch density on a full pitch, the team
 * attacking left to right. One hue, opacity = density (sequential scale).
 */
export function HeatmapPitch({ heatmap, showZones = true }: { heatmap: Heatmap; showZones?: boolean }) {
  const blurId = useId()
  // Scale to the 95th percentile so one hot cell doesn't wash out the rest.
  const sorted = heatmap.grid.filter((v) => v > 0).sort((a, b) => a - b)
  const cap = sorted[Math.floor(sorted.length * 0.95)] || 1
  const cw = PITCH_LENGTH / heatmap.cols
  const ch = PITCH_WIDTH / heatmap.rows
  const zones = heatmapZones(heatmap)

  return (
    <div className="space-y-3">
      <div className="relative">
        <FullPitch>
          <defs>
            <filter id={blurId} x="-10%" y="-10%" width="120%" height="120%">
              <feGaussianBlur stdDeviation="1.6" />
            </filter>
          </defs>
          <g filter={`url(#${blurId})`}>
            {heatmap.grid.map((v, i) =>
              v ? (
                <rect
                  key={i}
                  x={(i % heatmap.cols) * cw}
                  y={Math.floor(i / heatmap.cols) * ch}
                  width={cw + 0.2}
                  height={ch + 0.2}
                  fill="var(--chart-1)"
                  fillOpacity={Math.pow(Math.min(v / cap, 1), 1.3) * 0.95}
                />
              ) : null,
            )}
          </g>
        </FullPitch>
        <span className="absolute right-3 bottom-2 rounded bg-background/80 px-1.5 text-[0.7rem] font-medium text-muted-foreground">
          Ataque →
        </span>
      </div>
      {showZones && (
        <div className="grid gap-3 sm:grid-cols-2">
          <ZoneBar
            parts={[
              { label: "Propio", value: zones.own },
              { label: "Medio", value: zones.middle },
              { label: "Ataque", value: zones.attack },
            ]}
          />
          <ZoneBar
            parts={[
              { label: "Bandas", value: zones.wings },
              { label: "Centro", value: zones.center },
            ]}
          />
        </div>
      )}
    </div>
  )
}
