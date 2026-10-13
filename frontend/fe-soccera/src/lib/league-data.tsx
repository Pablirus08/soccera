import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react"
import { toast } from "sonner"

import { fetchSnapshot, isMock, syncLatestMatches } from "@/lib/api"
import { formatDateTime } from "@/lib/football"
import type { LeagueSnapshot } from "@/lib/types"

type LeagueDataState = {
  data: LeagueSnapshot | null
  error: string | null
  loading: boolean
  syncing: boolean
  syncMatches: () => Promise<void>
}

const LeagueDataContext = createContext<LeagueDataState | null>(null)

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

  const syncMatches = useCallback(async () => {
    setSyncing(true)
    try {
      const result = await syncLatestMatches()
      setData(await fetchSnapshot())
      const last = result.lastMatchDate ? ` · último partido: ${formatDateTime(result.lastMatchDate)}` : ""
      if (isMock) {
        toast.info("Modo demo: sin backend conectado", {
          description: `Se mostrarán datos reales al configurar VITE_API_URL${last}`,
        })
      } else {
        toast.success(`${result.synced} partidos sincronizados`, { description: `Datos al día${last}` })
      }
    } catch (e) {
      toast.error("No se pudieron actualizar los partidos", { description: (e as Error).message })
    } finally {
      setSyncing(false)
    }
  }, [])

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
