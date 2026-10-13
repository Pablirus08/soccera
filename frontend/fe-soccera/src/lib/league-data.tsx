import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react"
import { toast } from "sonner"

import { fetchSnapshot, fetchSyncStatus, isMock, syncLatestMatches } from "@/lib/api"
import { formatDateTime } from "@/lib/football"
import type { LeagueSnapshot, SyncStatus } from "@/lib/types"

type LeagueDataState = {
  data: LeagueSnapshot | null
  error: string | null
  loading: boolean
  syncing: boolean
  syncMatches: () => Promise<void>
}

const LeagueDataContext = createContext<LeagueDataState | null>(null)

function statusSummary(status: SyncStatus) {
  const parts = []
  if (status.last_match_date) parts.push(`Último partido: ${formatDateTime(status.last_match_date)}`)
  if (status.next_match_date) parts.push(`Próximo: ${formatDateTime(status.next_match_date)}`)
  return parts.join(" · ")
}

export function LeagueDataProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<LeagueSnapshot | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    fetchSnapshot()
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const runSync = useCallback(async (force: boolean) => {
    setSyncing(true)
    try {
      const result = await syncLatestMatches(force)
      setData(await fetchSnapshot())
      const { details_synced, status } = result
      const pending = status.details_pending
        ? ` Faltan ${status.details_pending}; vuelve a presionar para continuar.`
        : ""
      toast.success(
        details_synced
          ? `${details_synced} ${details_synced === 1 ? "partido actualizado" : "partidos actualizados"}`
          : "Calendario y resultados actualizados",
        { description: `${statusSummary(status)}${pending}` },
      )
    } catch (e) {
      toast.error("No se pudieron actualizar los partidos", { description: (e as Error).message })
    } finally {
      setSyncing(false)
    }
  }, [])

  /** Checks freshness first (no Sofascore call) and only syncs when something is stale. */
  const syncMatches = useCallback(async () => {
    setSyncing(true)
    let status: SyncStatus
    try {
      status = await fetchSyncStatus()
    } catch (e) {
      setSyncing(false)
      toast.error("No se pudo consultar el estado", { description: (e as Error).message })
      return
    }

    if (status.up_to_date) {
      setSyncing(false)
      toast.success("Todo está actualizado", {
        description: isMock ? "Modo demo: sin backend conectado" : statusSummary(status),
        action: isMock ? undefined : { label: "Forzar", onClick: () => runSync(true) },
      })
      return
    }
    await runSync(false)
  }, [runSync])

  return (
    <LeagueDataContext.Provider value={{ data, error, loading, syncing, syncMatches }}>
      {children}
    </LeagueDataContext.Provider>
  )
}

export function useLeagueData() {
  const ctx = useContext(LeagueDataContext)
  if (!ctx) throw new Error("useLeagueData must be used inside LeagueDataProvider")
  return ctx
}

/** For pages rendered by AppLayout, which only mounts them once data has loaded. */
export function useSnapshot() {
  const { data } = useLeagueData()
  if (!data) throw new Error("useSnapshot called before league data loaded")
  return data
}
