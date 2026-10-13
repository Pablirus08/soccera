// Mirrors the backend's Pydantic response models (backend/src/soccera/api/schemas.py),
// so swapping mocks for real API calls needs no shape changes.

export type TeamStanding = {
  team_id: number
  team_name: string
  played: number
  won: number
  drawn: number
  lost: number
  goals_for: number
  goals_against: number
  goal_diff: number
  points: number
}

export type Standings = {
  league_source_id: string
  season_year: number
  rows: TeamStanding[]
}

export type MatchStatus = "FINISHED" | "SCHEDULED" | "LIVE" | "POSTPONED" | "CANCELLED"

export type Match = {
  source_id: string
  round: string | null
  match_date: string
  status: MatchStatus | string
  home_team: string
  away_team: string
  home_score: number | null
  away_score: number | null
}

export type GoalStats = {
  matches_played: number
  total_goals: number
  avg_goals_per_match: number
  btts_pct: number
  over_2_5_pct: number
  home_win_pct: number
  draw_pct: number
  away_win_pct: number
}

export type TeamDiscipline = {
  team_id: number
  team_name: string
  yellow_cards: number
  red_cards: number
  total_cards: number
}

// Not served by the backend yet — players come from mocks/players.ts.
export type Position = "GK" | "DEF" | "MID" | "FWD"

export type PlayerStat = {
  id: string
  name: string
  team_name: string
  position: Position
  rating: number
  matches: number
  stats: { label: string; value: number }[]
}

export type LeagueSnapshot = {
  standings: Standings
  matches: Match[]
  upcoming: Match[]
  goals: GoalStats
  discipline: TeamDiscipline[]
  players: PlayerStat[]
  updatedAt: string
}

export type SyncResult = {
  synced: number
  lastMatchDate: string | null
}
