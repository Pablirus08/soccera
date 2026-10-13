import { Link } from "react-router"

import { FormPills } from "@/components/form-pills"
import { PageHeader } from "@/components/page-header"
import { TeamBadge } from "@/components/team-badge"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { recentForm, teamSlug } from "@/lib/football"
import { useSnapshot } from "@/lib/league-data"

export function TeamsPage() {
  const { standings, matches } = useSnapshot()

  return (
    <div className="space-y-6">
      <PageHeader title="Equipos" description="Elige un equipo para ver su análisis" />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {standings.rows.map((row, i) => (
          <Link key={row.team_id} to={`/equipos/${teamSlug(row.team_name)}`} className="group">
            <Card className="transition-colors group-hover:bg-muted/50">
              <CardHeader className="flex items-center justify-between">
                <TeamBadge team={row.team_name} size="lg" link={false} className="font-medium" />
                <span className="text-sm text-muted-foreground tabular-nums">{i + 1}.º</span>
              </CardHeader>
              <CardContent className="flex items-end justify-between gap-2">
                <dl className="grid grid-cols-3 gap-4 text-sm tabular-nums">
                  <div>
                    <dt className="text-xs text-muted-foreground">Pts</dt>
                    <dd className="font-semibold">{row.points}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted-foreground">G-E-P</dt>
                    <dd>{`${row.won}-${row.drawn}-${row.lost}`}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-muted-foreground">DG</dt>
                    <dd>{row.goal_diff > 0 ? `+${row.goal_diff}` : row.goal_diff}</dd>
                  </div>
                </dl>
                <FormPills form={recentForm(row.team_name, matches)} />
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
