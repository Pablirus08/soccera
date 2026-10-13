"""
Pydantic response models — mirror the analytics dataclasses field-for-field.
`from_attributes=True` lets FastAPI serialize the dataclasses returned by
soccera.analytics.* directly, no manual dict conversion needed.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SeasonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    year: int
    is_current: bool


class LeagueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    source: str
    source_id: str
    name: str
    country: str | None
    seasons: list[SeasonOut]


class TeamStandingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: int
    team_name: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_diff: int
    points: int


class StandingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    league_source_id: str
    season_year: int
    rows: list[TeamStandingOut]


class GoalStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    matches_played: int
    total_goals: int
    avg_goals_per_match: float
    btts_pct: float
    over_2_5_pct: float
    home_win_pct: float
    draw_pct: float
    away_win_pct: float


class TeamDisciplineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: int
    team_name: str
    yellow_cards: int
    red_cards: int
    total_cards: int


class TeamStatAveragesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: int
    team_name: str
    averages: dict[str, float]


class MatchListItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    source_id: str
    round: str | None
    match_date: datetime
    status: str
    home_team: str
    away_team: str
    home_score: int | None
    away_score: int | None


class MatchEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    minute: int
    extra_minute: int | None
    event_type: str
    event_detail: str | None
    team_name: str


class StatComparisonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    stat_type: str
    home_value: float | None
    away_value: float | None


class TeamInsightOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_name: str
    notes: list[str]


class MatchReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    match_source_id: str
    round: str | None
    match_date: datetime
    status: str
    home_team: str
    away_team: str
    home_score: int | None
    away_score: int | None
    home_score_ht: int | None
    away_score_ht: int | None
    events: list[MatchEventOut]
    stat_comparison: list[StatComparisonOut]
    home_insight: TeamInsightOut
    away_insight: TeamInsightOut


class PlayerSeasonStatsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_id: int
    name: str
    team_name: str
    position: str | None
    matches: int
    starts: int
    minutes: int
    rating: float | None
    adjusted_rating: float | None
    participation: float
    clean_sheets: int
    totals: dict[str, float]


class SyncStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    up_to_date: bool
    overdue_matches: int
    details_pending: int
    last_synced_at: datetime | None
    last_match_date: datetime | None
    next_match_date: datetime | None


class SyncResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    fixtures_synced: int
    details_synced: int
    status: SyncStatusOut


class MatchPredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    source_id: str
    round: str | None
    match_date: datetime
    home_team: str
    away_team: str
    expected_home_goals: float
    expected_away_goals: float
    home_win: float
    draw: float
    away_win: float
    likely_score: str
    likely_score_prob: float
    over_2_5: float
    both_score: float


class TeamRatingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: int
    team_name: str
    attack: float
    defense: float
    strength: float


class PredictionsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    trained_on: int
    home_advantage: float
    matches: list[MatchPredictionOut]
    ratings: list[TeamRatingOut]


class TeamProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: int
    team_name: str
    matches: int
    points: int
    expected_points: float
    goals_for: int
    goals_against: int
    xg_for: float
    xg_against: float
    possession: float
    per_match: dict[str, float]


class TeamMomentumOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: int
    team_name: str
    matches: int
    share: float
    spells_per_match: float
    avg_spell_minutes: float
    spell_conversion: float
    goals_in_spells_pct: float
    xg_per_spell: float
    rival_spells_per_match: float
    rival_spell_conversion: float
    goals_against_in_rival_spells_pct: float


class ShotPointOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    match_source_id: str
    minute: int
    added_time: int | None
    x: float
    y: float
    shot_type: str
    situation: str | None
    body_part: str | None
    xg: float | None
    xgot: float | None
    player_name: str | None
    team_name: str
    opponent_name: str


class ShotSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    shots: int
    goals: int
    on_target: int
    xg: float
    inside_box_pct: float
    xg_per_shot: float


class HeatmapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cols: int
    rows: int
    grid: list[int]
    matches: int


class TeamVisualsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_id: int
    team_name: str
    shots_for: list[ShotPointOut]
    shots_against: list[ShotPointOut]
    summary_for: ShotSummaryOut
    summary_against: ShotSummaryOut
    heatmap: HeatmapOut


class SpellOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    start: float
    end: float
    minutes: float


class SideMomentumOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_name: str
    spells: list[SpellOut]
    spells_converted: int
    share: float
    xg_in_spells: float


class GoalMarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    minute: float
    label: str
    team_name: str
    player_name: str | None


class MatchVisualsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    source_id: str
    round: str | None
    match_date: datetime
    status: str
    home_team: str
    away_team: str
    home_score: int | None
    away_score: int | None
    momentum: list[list[float]]
    goals: list[GoalMarkOut]
    home_momentum: SideMomentumOut | None
    away_momentum: SideMomentumOut | None
    shots: list[ShotPointOut]
    home_heatmap: HeatmapOut | None
    away_heatmap: HeatmapOut | None
    xg_home: float
    xg_away: float


class H2HMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    source_id: str
    match_date: datetime
    tournament: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int


class H2HPredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    home_team: str
    away_team: str
    home_win: float
    draw: float
    away_win: float
    expected_home_goals: float
    expected_away_goals: float


class HeadToHeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_a: str
    team_b: str
    played: int
    a_wins: int
    draws: int
    b_wins: int
    a_goals: int
    b_goals: int
    matches: list[H2HMatchOut]
    a_home: H2HPredictionOut
    b_home: H2HPredictionOut
