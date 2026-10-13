import { Link } from "react-router"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { playerInitials, POSITION_LABELS, POSITION_SHORT, shortName, teamSlug } from "@/lib/football"
import type { PlayerStat, Position } from "@/lib/types"

const POSITIONS: Position[] = ["GK", "DEF", "MID", "FWD"]

function PlayerRow({ player, rank }: { player: PlayerStat; rank: number }) {
  return (
    <li className="flex items-center gap-3 py-2.5">
      <span className="w-4 text-center text-xs text-muted-foreground tabular-nums">{rank}</span>
      <Avatar>
        <AvatarFallback className="text-xs">{playerInitials(player.name)}</AvatarFallback>
      </Avatar>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium">{player.name}</p>
        <p className="truncate text-xs text-muted-foreground">
          <Link to={`/equipos/${teamSlug(player.team_name)}`} className="hover:underline">
            {shortName(player.team_name)}
          </Link>
          <span className="tabular-nums">
            {" "}· {player.matches} PJ · {player.minutes}&#8242;
          </span>
        </p>
      </div>
      <div className="hidden gap-4 text-right sm:flex">
        {player.stats.map((s) => (
          <div key={s.label} className="w-20">
            <p className="text-sm font-medium tabular-nums">{s.value}</p>
            <p className="truncate text-[0.7rem] text-muted-foreground">{s.label}</p>
          </div>
        ))}
      </div>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="cursor-help rounded-md bg-primary px-2 py-1 text-xs font-semibold text-primary-foreground tabular-nums">
            {player.rating.toFixed(2)}
          </span>
        </TooltipTrigger>
        <TooltipContent side="left" className="max-w-56">
          Nivel ajustado {player.rating.toFixed(2)} · promedio simple{" "}
          {player.avgRating.toFixed(2)} en {player.matches} PJ. Pocos partidos pesan menos.
        </TooltipContent>
      </Tooltip>
    </li>
  )
}

/** Best players split by position, ranked by adjusted level (see PlayerStat.rating). */
export function TopPlayers({ players, limit = 5 }: { players: PlayerStat[]; limit?: number }) {
  return (
    <Tabs defaultValue="FWD">
      <TabsList className="w-full">
        {POSITIONS.map((p) => (
          <TabsTrigger key={p} value={p}>
            <span className="sm:hidden">{POSITION_SHORT[p]}</span>
            <span className="hidden sm:inline">{POSITION_LABELS[p]}</span>
          </TabsTrigger>
        ))}
      </TabsList>
      {POSITIONS.map((p) => (
        <TabsContent key={p} value={p}>
          <ul className="divide-y">
            {players
              .filter((pl) => pl.position === p)
              .sort((a, b) => b.rating - a.rating)
              .slice(0, limit)
              .map((pl, i) => (
                <PlayerRow key={pl.id} player={pl} rank={i + 1} />
              ))}
          </ul>
        </TabsContent>
      ))}
    </Tabs>
  )
}
