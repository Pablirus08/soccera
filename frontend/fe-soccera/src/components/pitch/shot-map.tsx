import { useState } from "react"

import { HalfPitch, PITCH_LENGTH, PITCH_WIDTH } from "@/components/pitch/pitch"
import type { ShotPoint, ShotSummary } from "@/lib/types"

/** Outcome encoded by fill + outline (not color alone); `color` is the team's series color. */
const shotStyles = (color: string) => ({
  goal: { label: "Gol", fill: color, fillOpacity: 1, stroke: "var(--background)" },
  onTarget: { label: "Atajado", fill: color, fillOpacity: 0.3, stroke: color },
  off: { label: "Desviado / bloqueado", fill: "none", fillOpacity: 0, stroke: "var(--muted-foreground)" },
})

const styleFor = (s: ShotPoint, styles: ReturnType<typeof shotStyles>) =>
  s.shot_type === "goal" ? styles.goal : s.shot_type === "save" ? styles.onTarget : styles.off

// Circle area grows with xG; the floor keeps tiny-xG shots visible.
const radius = (xg: number | null) => 0.9 + Math.sqrt(xg ?? 0) * 3.4

const SHOT_TYPE_LABEL: Record<string, string> = {
  goal: "Gol",
  save: "Atajado",
  miss: "Desviado",
  block: "Bloqueado",
  post: "Al poste",
}

const SITUATION_LABEL: Record<string, string> = {
  regular: "Jugada",
  corner: "Córner",
  "free-kick": "Tiro libre",
  "set-piece": "Balón parado",
  "throw-in-set-piece": "Saque de banda",
  penalty: "Penal",
  "fast-break": "Contragolpe",
  assisted: "Jugada",
}

const toPitch = (s: ShotPoint) => ({
  cx: (s.y / 100) * PITCH_WIDTH,
  cy: Math.min((s.x / 100) * PITCH_LENGTH, PITCH_LENGTH / 2),
})

// 16.5 m box on a ~105 m pitch, in the same 0-100 units as ShotPoint.x.
const BOX_DEPTH_PCT = 15.7

/** Same aggregates the backend's summarize_shots returns, for client-side subsets. */
export function summarizeShots(shots: ShotPoint[]): ShotSummary {
  const xg = shots.reduce((a, s) => a + (s.xg ?? 0), 0)
  const n = shots.length
  return {
    shots: n,
    goals: shots.filter((s) => s.shot_type === "goal").length,
    on_target: shots.filter((s) => s.shot_type === "goal" || s.shot_type === "save").length,
    xg,
    xg_per_shot: n ? xg / n : 0,
    inside_box_pct: n ? shots.filter((s) => s.x <= BOX_DEPTH_PCT).length / n : 0,
  }
}

export function ShotSummaryRow({ summary }: { summary: ShotSummary }) {
  const items = [
    ["Tiros", summary.shots],
    ["Goles", summary.goals],
    ["Al arco", summary.on_target],
    ["xG", summary.xg.toFixed(1)],
    ["xG/tiro", summary.xg_per_shot.toFixed(2)],
    ["En el área", `${Math.round(summary.inside_box_pct * 100)}%`],
  ] as const
  return (
    <dl className="grid grid-cols-3 gap-2 text-center sm:grid-cols-6">
      {items.map(([label, value]) => (
        <div key={label}>
          <dt className="text-[0.7rem] text-muted-foreground">{label}</dt>
          <dd className="text-sm font-semibold tabular-nums">{value}</dd>
        </div>
      ))}
    </dl>
  )
}

/** Half-pitch shot map; the attacked goal is at the top. */
export function ShotMap({
  shots,
  color = "var(--chart-1)",
  className,
}: {
  shots: ShotPoint[]
  color?: string
  className?: string
}) {
  const [hover, setHover] = useState<number | null>(null)
  const styles = shotStyles(color)
  // Draw goals last so they sit on top.
  const ordered = shots
    .map((s, i) => ({ s, i }))
    .sort((a, b) => Number(a.s.shot_type === "goal") - Number(b.s.shot_type === "goal"))
  const active = hover !== null ? shots[hover] : null

  return (
    <div className={className}>
      <div className="relative">
        <HalfPitch>
          {ordered.map(({ s, i }) => {
            const { cx, cy } = toPitch(s)
            const st = styleFor(s, styles)
            const r = radius(s.xg)
            return (
              <g key={i} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)}>
                <circle
                  cx={cx}
                  cy={cy}
                  r={r}
                  fill={st.fill}
                  fillOpacity={st.fillOpacity}
                  stroke={st.stroke}
                  strokeWidth={hover === i ? 0.7 : 0.35}
                />
                {/* Larger invisible hit target than the mark itself. */}
                <circle cx={cx} cy={cy} r={Math.max(r, 2.4)} fill="transparent" />
              </g>
            )
          })}
        </HalfPitch>
        {active && (
          <div
            className="pointer-events-none absolute z-10 w-max max-w-52 -translate-x-1/2 -translate-y-[calc(100%+10px)] rounded-lg border bg-background px-2.5 py-1.5 text-xs shadow-md"
            style={{
              left: `${((toPitch(active).cx + 2) / (PITCH_WIDTH + 4)) * 100}%`,
              top: `${((toPitch(active).cy + 3) / (PITCH_LENGTH / 2 + 5)) * 100}%`,
            }}
          >
            <p className="font-medium">{active.player_name ?? "Jugador desconocido"}</p>
            <p className="text-muted-foreground">
              {active.minute}
              {active.added_time ? `+${active.added_time}` : ""}&#8242; · {SHOT_TYPE_LABEL[active.shot_type] ?? active.shot_type}
              {active.situation ? ` · ${SITUATION_LABEL[active.situation] ?? active.situation}` : ""}
            </p>
            <p className="tabular-nums text-muted-foreground">
              xG {active.xg?.toFixed(2) ?? "–"}
              {active.xgot != null ? ` · xGOT ${active.xgot.toFixed(2)}` : ""} · vs {active.opponent_name}
            </p>
          </div>
        )}
      </div>
      <div className="mt-2 flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
        {Object.values(styles).map((st) => (
          <span key={st.label} className="flex items-center gap-1.5">
            <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden>
              <circle cx="6" cy="6" r="4.5" fill={st.fill} fillOpacity={st.fillOpacity} stroke={st.stroke} strokeWidth="1.2" />
            </svg>
            {st.label}
          </span>
        ))}
        <span>· tamaño = xG</span>
      </div>
    </div>
  )
}
