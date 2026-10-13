import { useState } from "react"

import { TeamMomentumCard } from "@/components/analysis/team-profile-card"
import { AsyncBlock } from "@/components/async-block"
import { HeatmapPitch } from "@/components/pitch/heatmap"
import { ShotMap, ShotSummaryRow } from "@/components/pitch/shot-map"
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useAsync } from "@/hooks/use-async"
import { fetchTeamVisuals } from "@/lib/api"
import { useSnapshot } from "@/lib/league-data"
import type { TeamVisuals } from "@/lib/types"

function ShotMapCard({ v }: { v: TeamVisuals }) {
  const [side, setSide] = useState<"for" | "against">("for")
  const shots = side === "for" ? v.shots_for : v.shots_against
  const summary = side === "for" ? v.summary_for : v.summary_against

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mapa de tiros</CardTitle>
        <CardDescription>
          {side === "for" ? "Sus remates en la temporada" : "Remates que recibió en la temporada"}
        </CardDescription>
        <CardAction>
          <Tabs value={side} onValueChange={(s) => setSide(s as "for" | "against")}>
            <TabsList>
              <TabsTrigger value="for">A favor</TabsTrigger>
              <TabsTrigger value="against">En contra</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardAction>
      </CardHeader>
      <CardContent className="space-y-3">
        <ShotSummaryRow summary={summary} />
        <ShotMap shots={shots} className="mx-auto max-w-md" />
      </CardContent>
    </Card>
  )
}

/** Season shot map, touch heatmap and momentum profile for one team. */
export function TeamVisualsSection({ teamId }: { teamId: number }) {
  const { momentum } = useSnapshot()
  const state = useAsync(`team-${teamId}`, () => fetchTeamVisuals(teamId))
  const teamMomentum = momentum.find((t) => t.team_id === teamId)

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <AsyncBlock {...state} skeletonClassName="h-[32rem]">
          {(v) => <ShotMapCard v={v} />}
        </AsyncBlock>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Dónde domina la pelota</CardTitle>
              <CardDescription>
                Zonas donde más toca la pelota (sin el portero), atacando hacia la derecha
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AsyncBlock {...state} skeletonClassName="h-56">
                {(v) =>
                  v.heatmap.matches ? (
                    <HeatmapPitch heatmap={v.heatmap} />
                  ) : (
                    <p className="text-sm text-muted-foreground">Sin datos de mapa de calor.</p>
                  )
                }
              </AsyncBlock>
            </CardContent>
          </Card>

          {teamMomentum && (
            <Card>
              <CardHeader>
                <CardTitle>Momentum</CardTitle>
                <CardDescription>Cuánto domina los partidos y cuánto lo aprovecha (y su rival)</CardDescription>
              </CardHeader>
              <CardContent>
                <TeamMomentumCard team={teamMomentum} all={momentum} />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
