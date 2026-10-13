import { TeamBadge } from "@/components/team-badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { TeamMomentum } from "@/lib/types"

const pct = (v: number) => `${Math.round(v * 100)}%`

/** Share bar: one hue, length = value (0-100%), with the number printed beside it. */
function ShareBar({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 flex-1 rounded-full bg-muted">
        <div className="h-full rounded-full bg-chart-1" style={{ width: `${value * 100}%` }} />
      </div>
      <span className="w-9 text-right text-xs font-medium">{pct(value)}</span>
    </div>
  )
}

/** League-wide momentum: who dominates, and who converts (or concedes from) spells. */
export function MomentumTable({ teams }: { teams: TeamMomentum[] }) {
  return (
    <Table className="tabular-nums">
      <TableHeader>
        <TableRow>
          <TableHead>Equipo</TableHead>
          <TableHead className="w-[22%] min-w-28" title="Parte del partido con la presión a su favor">Tiempo con momentum</TableHead>
          <TableHead className="text-center" title="Rachas de dominio (4+ min) por partido">Rachas/PJ</TableHead>
          <TableHead className="text-center" title="Rachas propias que terminan en gol">Aprovecha</TableHead>
          <TableHead className="hidden text-center md:table-cell" title="xG generado por racha">xG/racha</TableHead>
          <TableHead className="text-center" title="Rachas del rival por partido">Rival rachas/PJ</TableHead>
          <TableHead className="text-center" title="Rachas del rival que terminan en gol en contra">Rival aprovecha</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {teams.map((t) => (
          <TableRow key={t.team_id}>
            <TableCell className="max-w-44 font-medium">
              <TeamBadge team={t.team_name} short />
            </TableCell>
            <TableCell>
              <ShareBar value={t.share} />
            </TableCell>
            <TableCell className="text-center">{t.spells_per_match.toFixed(1)}</TableCell>
            <TableCell className="text-center font-medium">{pct(t.spell_conversion)}</TableCell>
            <TableCell className="hidden text-center md:table-cell text-muted-foreground">{t.xg_per_spell.toFixed(2)}</TableCell>
            <TableCell className="text-center">{t.rival_spells_per_match.toFixed(1)}</TableCell>
            <TableCell className="text-center font-medium">{pct(t.rival_spell_conversion)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
