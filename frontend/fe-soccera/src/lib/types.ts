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

/** GET /api/players — season aggregates per player. */
export type PlayerSeasonStats = {
  player_id: number
  name: string
  team_name: string
  position: "Goalkeeper" | "Defender" | "Midfielder" | "Attacker" | null
  matches: number
  starts: number
  minutes: number
  rating: number | null
  adjusted_rating: number | null
  participation: number
  clean_sheets: number
  totals: Record<string, number>
}

/** GET /api/sync/status — database-only freshness check. */
export type SyncStatus = {
  up_to_date: boolean
  overdue_matches: number
  details_pending: number
  last_synced_at: string | null
  last_match_date: string | null
  next_match_date: string | null
}

/** POST /api/sync */
export type SyncResult = {
  fixtures_synced: number
  details_synced: number
  status: SyncStatus
}

/** GET /api/teams/profiles — xG-based team profile (matches with stats only). */
export type TeamProfile = {
  team_id: number
  team_name: string
  matches: number
  points: number
  expected_points: number
  goals_for: number
  goals_against: number
  xg_for: number
  xg_against: number
  possession: number
  per_match: {
    xg_for: number
    xg_against: number
    shots_for: number
    shots_against: number
    shots_on_target_for: number
    xg_per_shot: number
  }
}

export type MatchPrediction = {
  source_id: string
  round: string | null
  match_date: string
  home_team: string
  away_team: string
  expected_home_goals: number
  expected_away_goals: number
  home_win: number
  draw: number
  away_win: number
  likely_score: string
  likely_score_prob: number
  over_2_5: number
  both_score: number
}

export type TeamRating = {
  team_id: number
  team_name: string
  attack: number
  defense: number
  strength: number
}

/** GET /api/predictions — Poisson model output for the next round. */
export type Predictions = {
  trained_on: number
  home_advantage: number
  matches: MatchPrediction[]
  ratings: TeamRating[]
}

// Frontend shape for the "best players" UI (mapped from PlayerSeasonStats).
export type Position = "GK" | "DEF" | "MID" | "FWD"

export type PlayerStat = {
  id: string
  name: string
  team_name: string
  position: Position
  /** Adjusted level (ranking key): minutes-weighted, shrunk toward the position mean. */
  rating: number
  /** Plain mean of match ratings. */
  avgRating: number
  matches: number
  minutes: number
  stats: { label: string; value: number }[]
}

export type LeagueSnapshot = {
  standings: Standings
  matches: Match[]
  upcoming: Match[]
  goals: GoalStats
  discipline: TeamDiscipline[]
  /** Ranking-eligible players, mapped for the "best players" UI. */
  players: PlayerStat[]
  /** Every player with minutes, raw season aggregates (for leaderboards). */
  playerSeason: PlayerSeasonStats[]
  profiles: TeamProfile[]
  predictions: Predictions
  momentum: TeamMomentum[]
  updatedAt: string | null
}

/** GET /api/momentum — dominance spells and how they're converted. */
export type TeamMomentum = {
  team_id: number
  team_name: string
  matches: number
  share: number
  spells_per_match: number
  avg_spell_minutes: number
  spell_conversion: number
  goals_in_spells_pct: number
  xg_per_spell: number
  rival_spells_per_match: number
  rival_spell_conversion: number
  goals_against_in_rival_spells_pct: number
}

/** x = distance from the attacked goal, y = width; both 0-100 % of the pitch. */
export type ShotPoint = {
  match_source_id: string
  minute: number
  added_time: number | null
  x: number
  y: number
  shot_type: "goal" | "save" | "miss" | "block" | "post" | string
  situation: string | null
  body_part: string | null
  xg: number | null
  xgot: number | null
  player_name: string | null
  team_name: string
  opponent_name: string
}

export type ShotSummary = {
  shots: number
  goals: number
  on_target: number
  xg: number
  inside_box_pct: number
  xg_per_shot: number
}

/** rows x cols touch counts, row-major; the team attacks toward the last column. */
export type Heatmap = { cols: number; rows: number; grid: number[]; matches: number }

export type TeamVisuals = {
  team_id: number
  team_name: string
  shots_for: ShotPoint[]
  shots_against: ShotPoint[]
  summary_for: ShotSummary
  summary_against: ShotSummary
  heatmap: Heatmap
}

export type Spell = { start: number; end: number; minutes: number }

export type SideMomentum = {
  team_name: string
  spells: Spell[]
  spells_converted: number
  share: number
  xg_in_spells: number
}

export type MatchVisuals = {
  source_id: string
  round: string | null
  match_date: string
  status: string
  home_team: string
  away_team: string
  home_score: number | null
  away_score: number | null
  /** [[minute, value]]: value > 0 = home team pressing. */
  momentum: [number, number][]
  goals: { minute: number; label: string; team_name: string; player_name: string | null }[]
  home_momentum: SideMomentum | null
  away_momentum: SideMomentum | null
  shots: ShotPoint[]
  home_heatmap: Heatmap | null
  away_heatmap: Heatmap | null
  xg_home: number
  xg_away: number
}

export type H2HPrediction = {
  home_team: string
  away_team: string
  home_win: number
  draw: number
  away_win: number
  expected_home_goals: number
  expected_away_goals: number
}

export type HeadToHead = {
  team_a: string
  team_b: string
  played: number
  a_wins: number
  draws: number
  b_wins: number
  a_goals: number
  b_goals: number
  matches: {
    source_id: string
    match_date: string
    tournament: string
    home_team: string
    away_team: string
    home_score: number
    away_score: number
  }[]
  a_home: H2HPrediction
  b_home: H2HPrediction
}
