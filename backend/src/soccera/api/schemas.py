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
