import disciplineMock from "@/mocks/discipline.json"
import goalsMock from "@/mocks/goals.json"
import matchesMock from "@/mocks/matches.json"
import { playersMock } from "@/mocks/players"
import standingsMock from "@/mocks/standings.json"
import upcomingMock from "@/mocks/upcoming.json"
import { nextRoundFixtures } from "@/lib/football"
import type {
  GoalStats,
  LeagueSnapshot,
  Match,
  PlayerSeasonStats,
  PlayerStat,
  Position,
  Standings,
  SyncResult,
  SyncStatus,
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

// Players who played less than this share of their team's minutes are left out of rankings.
export const MIN_PLAYER_PARTICIPATION = 0.3

const MOCK_UPDATED_AT = "2026-10-13T18:15:00Z"

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

const leagueQuery = `league=${LEAGUE.sourceId}&season=${LEAGUE.season}`

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}/api${path}`, init)
  if (!response.ok) {
    // FastAPI errors carry a human-readable {"detail": "..."}.
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail ?? `${response.status} ${response.statusText}`)
  }
  return response.json() as Promise<T>
}

const POSITIONS: Record<NonNullable<PlayerSeasonStats["position"]>, Position> = {
  Goalkeeper: "GK",
  Defender: "DEF",
  Midfielder: "MID",
  Attacker: "FWD",
}

/** The two headline stats shown next to each player, per position. */
function headlineStats(p: PlayerSeasonStats, position: Position): PlayerStat["stats"] {
  const t = p.totals
  switch (position) {
    case "GK":
      return [
        { label: "Vallas invictas", value: p.clean_sheets },
        { label: "Atajadas", value: t.saves ?? 0 },
      ]
    case "DEF":
      return [
        { label: "Despejes", value: t.totalClearance ?? 0 },
        { label: "Intercepciones", value: t.interceptionWon ?? 0 },
      ]
    case "MID":
      return [
        { label: "Asistencias", value: t.goalAssist ?? 0 },
        { label: "Pases clave", value: t.keyPass ?? 0 },
      ]
    case "FWD":
      return [
        { label: "Goles", value: t.goals ?? 0 },
        { label: "Tiros al arco", value: t.onTargetScoringAttempt ?? 0 },
      ]
  }
}

function toPlayerStat(p: PlayerSeasonStats): PlayerStat | null {
  const position = p.position ? POSITIONS[p.position] : undefined
  if (!position || p.rating === null || p.adjusted_rating === null) return null
  return {
    id: String(p.player_id),
    name: p.name,
    team_name: p.team_name,
    position,
    rating: p.adjusted_rating,
    avgRating: p.rating,
    matches: p.matches,
    minutes: p.minutes,
    stats: headlineStats(p, position),
  }
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

  const [standings, matches, goals, discipline, players, status] = await Promise.all([
    request<Standings>(`/standings?${leagueQuery}`),
    request<Match[]>(`/matches?${leagueQuery}`),
    request<GoalStats>(`/goals?${leagueQuery}`),
    request<TeamDiscipline[]>(`/discipline?${leagueQuery}`),
    request<PlayerSeasonStats[]>(`/players?${leagueQuery}&min_participation=${MIN_PLAYER_PARTICIPATION}`),
    fetchSyncStatus(),
  ])
  return {
    standings,
    matches,
    upcoming: nextRoundFixtures(matches),
    goals,
    discipline,
    players: players.map(toPlayerStat).filter((p): p is PlayerStat => p !== null),
    updatedAt: status.last_synced_at,
  }
}

/** Database-only check on the backend — never reaches Sofascore. */
export async function fetchSyncStatus(): Promise<SyncStatus> {
  if (isMock) {
    await delay(200)
    return {
      up_to_date: true,
      overdue_matches: 0,
      details_pending: 0,
      last_synced_at: MOCK_UPDATED_AT,
      last_match_date: "2026-10-11T23:00:00Z",
      next_match_date: (upcomingMock as Match[])[0]?.match_date ?? null,
    }
  }
  return request<SyncStatus>(`/sync/status?${leagueQuery}`)
}

/**
 * Pulls the latest fixtures and match detail from Sofascore through the
 * backend. `force` skips the backend's own "already up to date" short-circuit.
 */
export async function syncLatestMatches(force = false): Promise<SyncResult> {
  if (isMock) {
    await delay(1500)
    return { fixtures_synced: 0, details_synced: 0, status: await fetchSyncStatus() }
  }
  return request<SyncResult>(`/sync?${leagueQuery}${force ? "&force=true" : ""}`, {
    method: "POST",
  })
}
