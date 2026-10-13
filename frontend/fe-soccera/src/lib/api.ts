import disciplineMock from "@/mocks/discipline.json"
import goalsMock from "@/mocks/goals.json"
import matchesMock from "@/mocks/matches.json"
import { playersMock } from "@/mocks/players"
import standingsMock from "@/mocks/standings.json"
import upcomingMock from "@/mocks/upcoming.json"
import type {
  GoalStats,
  LeagueSnapshot,
  Match,
  Standings,
  SyncResult,
  TeamDiscipline,
} from "@/lib/types"

// Set VITE_API_URL (e.g. http://localhost:8000) in .env.local to use the
// FastAPI backend. Without it the app runs entirely on the JSON snapshot in
// src/mocks (real Apertura 2026 data exported on 2026-10-13).
const API_URL = import.meta.env.VITE_API_URL as string | undefined
export const isMock = !API_URL

export const LEAGUE = {
  sourceId: "11535",
  season: 2026,
  name: "Primera División",
  tournament: "Apertura 2026",
}

const MOCK_UPDATED_AT = "2026-10-13T18:15:00Z"

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}/api${path}`, init)
  if (!response.ok) throw new Error(`${response.status} ${response.statusText} — ${path}`)
  return response.json() as Promise<T>
}

export async function fetchSnapshot(): Promise<LeagueSnapshot> {
  if (isMock) {
    await delay(250)
    return {
      standings: standingsMock as Standings,
      matches: matchesMock as Match[],
      upcoming: upcomingMock as Match[],
      goals: goalsMock as GoalStats,
      discipline: disciplineMock as TeamDiscipline[],
      players: playersMock,
      updatedAt: MOCK_UPDATED_AT,
    }
  }

  const q = `?league=${LEAGUE.sourceId}&season=${LEAGUE.season}`
  const [standings, matches, goals, discipline] = await Promise.all([
    request<Standings>(`/standings${q}`),
    request<Match[]>(`/matches${q}`),
    request<GoalStats>(`/goals${q}`),
    request<TeamDiscipline[]>(`/discipline${q}`),
  ])
  return {
    standings,
    matches,
    goals,
    discipline,
    // TODO(backend): the adapter only syncs past events (events/last); add
    // events/next so upcoming fixtures come from /matches too.
    upcoming: upcomingMock as Match[],
    // TODO(backend): no player data yet.
    players: playersMock,
    updatedAt: new Date().toISOString(),
  }
}

/**
 * "Actualizar partidos": asks the backend to pull the latest matches from
 * Sofascore (run_backfill_sofascore + sync_match_details for the current
 * season). TODO(backend): expose this as POST /api/sync.
 */
export async function syncLatestMatches(): Promise<SyncResult> {
  if (isMock) {
    await delay(1500)
    const lastMatchDate = (matchesMock as Match[])
      .filter((m) => m.status === "FINISHED")
      .reduce<string | null>((max, m) => (max && max > m.match_date ? max : m.match_date), null)
    return { synced: 0, lastMatchDate }
  }
  return request<SyncResult>(`/sync?league=${LEAGUE.sourceId}&season=${LEAGUE.season}`, {
    method: "POST",
  })
}
