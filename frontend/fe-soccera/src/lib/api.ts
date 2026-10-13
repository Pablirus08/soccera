import disciplineMock from "@/mocks/discipline.json"
import goalsMock from "@/mocks/goals.json"
import matchesMock from "@/mocks/matches.json"
import momentumMock from "@/mocks/momentum.json"
import playersMock from "@/mocks/players.json"
import predictionsMock from "@/mocks/predictions.json"
import profilesMock from "@/mocks/profiles.json"
import standingsMock from "@/mocks/standings.json"
import statusMock from "@/mocks/status.json"
import { nextRoundFixtures } from "@/lib/football"
import type {
  GoalStats,
  HeadToHead,
  LeagueSnapshot,
  Match,
  MatchVisuals,
  PlayerSeasonStats,
  PlayerStat,
  Position,
  Predictions,
  Standings,
  SyncResult,
  SyncStatus,
  TeamDiscipline,
  TeamMomentum,
  TeamProfile,
  TeamVisuals,
} from "@/lib/types"

// Set VITE_API_URL (e.g. http://localhost:8000) in .env.local to use the
// FastAPI backend. Without it the app runs on src/mocks: raw API responses
// for Apertura 2026 saved on 2026-10-13 (same shapes as the live backend).
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

/** Raw backend responses that make up one page load. */
type ApiPayload = {
  standings: Standings
  matches: Match[]
  goals: GoalStats
  discipline: TeamDiscipline[]
  players: PlayerSeasonStats[]
  profiles: TeamProfile[]
  predictions: Predictions
  momentum: TeamMomentum[]
  status: SyncStatus
}

function toSnapshot(p: ApiPayload, now: Date): LeagueSnapshot {
  return {
    standings: p.standings,
    matches: p.matches,
    upcoming: nextRoundFixtures(p.matches, now),
    goals: p.goals,
    discipline: p.discipline,
    players: p.players
      .filter((pl) => pl.participation >= MIN_PLAYER_PARTICIPATION)
      .map(toPlayerStat)
      .filter((pl): pl is PlayerStat => pl !== null),
    playerSeason: p.players,
    profiles: p.profiles,
    predictions: p.predictions,
    momentum: p.momentum,
    updatedAt: p.status.last_synced_at,
  }
}

const mockPayload = (): ApiPayload => ({
  standings: standingsMock as Standings,
  matches: matchesMock as Match[],
  goals: goalsMock as GoalStats,
  discipline: disciplineMock as TeamDiscipline[],
  players: playersMock as PlayerSeasonStats[],
  profiles: profilesMock as TeamProfile[],
  predictions: predictionsMock as Predictions,
  momentum: momentumMock as TeamMomentum[],
  status: statusMock as SyncStatus,
})

export async function fetchSnapshot(): Promise<LeagueSnapshot> {
  if (isMock) {
    await delay(250)
    // Mock fixtures are frozen in time: "upcoming" is relative to the export.
    return toSnapshot(mockPayload(), new Date(statusMock.last_synced_at ?? Date.now()))
  }

  const [standings, matches, goals, discipline, players, profiles, predictions, momentum, status] =
    await Promise.all([
      request<Standings>(`/standings?${leagueQuery}`),
      request<Match[]>(`/matches?${leagueQuery}`),
      request<GoalStats>(`/goals?${leagueQuery}`),
      request<TeamDiscipline[]>(`/discipline?${leagueQuery}`),
      request<PlayerSeasonStats[]>(`/players?${leagueQuery}`),
      request<TeamProfile[]>(`/teams/profiles?${leagueQuery}`),
      request<Predictions>(`/predictions?${leagueQuery}`),
      request<TeamMomentum[]>(`/momentum?${leagueQuery}`),
      fetchSyncStatus(),
    ])
  return toSnapshot(
    { standings, matches, goals, discipline, players, profiles, predictions, momentum, status },
    new Date(),
  )
}

/** Database-only check on the backend — never reaches Sofascore. */
export async function fetchSyncStatus(): Promise<SyncStatus> {
  if (isMock) {
    await delay(200)
    return statusMock as SyncStatus
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

/** Thrown by on-demand detail fetches in demo mode, which has no per-team/match data. */
export class DemoModeError extends Error {
  constructor() {
    super("Disponible solo con el backend conectado")
  }
}

function detail<T>(path: string): Promise<T> {
  return isMock ? Promise.reject(new DemoModeError()) : request<T>(path)
}

export const fetchTeamVisuals = (teamId: number) =>
  detail<TeamVisuals>(`/teams/${teamId}/visuals?${leagueQuery}`)

export const fetchMatchVisuals = (sourceId: string) =>
  detail<MatchVisuals>(`/matches/${sourceId}/visuals`)

export const fetchHeadToHead = (teamA: number, teamB: number) =>
  detail<HeadToHead>(`/h2h?team_a=${teamA}&team_b=${teamB}`)
