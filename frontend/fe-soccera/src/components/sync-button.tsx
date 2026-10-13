import { RefreshCwIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { useLeagueData } from "@/lib/league-data"
import { cn } from "@/lib/utils"

/** Pulls the latest matches through the backend (see syncLatestMatches in lib/api). */
export function SyncButton() {
  const { syncing, syncMatches, loading } = useLeagueData()

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button onClick={syncMatches} disabled={syncing || loading} size="sm" aria-label="Actualizar partidos">
          <RefreshCwIcon className={cn(syncing && "animate-spin")} data-icon="inline-start" />
          <span className="hidden sm:inline">{syncing ? "Actualizando…" : "Actualizar partidos"}</span>
        </Button>
      </TooltipTrigger>
      <TooltipContent>Trae los resultados más recientes desde Sofascore</TooltipContent>
    </Tooltip>
  )
}
