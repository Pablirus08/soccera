"""
Canonical, source-agnostic representations of soccer data.

Every DataSourceAdapter (API-Football today, a Costa Rican League scraper
later) returns these models. Nothing outside ingestion/providers/ should
ever see a provider's raw response shape — storage and sync code only
depend on what's defined here.
"""

from datetime import date, datetime

from pydantic import BaseModel


class DomainVenue(BaseModel):
    source_id: str
    name: str
    city: str | None = None
    country: str | None = None
    capacity: int | None = None


class DomainLeague(BaseModel):
    source_id: str
    name: str
    country: str | None = None
    type: str = "league"


class DomainSeason(BaseModel):
    league_source_id: str
    year: int
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool = False


class DomainLeagueWithSeasons(BaseModel):
    league: DomainLeague
    seasons: list[DomainSeason] = []


class DomainTeam(BaseModel):
    source_id: str
    name: str
    short_name: str | None = None
    country: str | None = None
    founded: int | None = None
    venue: DomainVenue | None = None


class DomainPlayer(BaseModel):
    source_id: str
    name: str
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    nationality: str | None = None
    position: str | None = None
    shirt_number: int | None = None


class DomainMatch(BaseModel):
    source_id: str
    league_source_id: str
    season_year: int
    home_team_source_id: str
    away_team_source_id: str
    venue_source_id: str | None = None
    match_date: datetime
    status: str
    elapsed_minutes: int | None = None
    round: str | None = None
    referee: str | None = None
    home_score: int | None = None
    away_score: int | None = None
    home_score_ht: int | None = None
    away_score_ht: int | None = None


class DomainMatchStatistic(BaseModel):
    match_source_id: str
    team_source_id: str
    stat_type: str
    stat_value: float | None = None


class DomainPlayerMatchStat(BaseModel):
    """One player's appearance in one match: lineup role plus their stat line.
    `stats` holds every numeric stat the provider reports (passes, saves,
    expected goals, ...) keyed by the provider's stat name."""

    match_source_id: str
    team_source_id: str
    player: DomainPlayer
    is_starter: bool
    shirt_number: int | None = None
    position: str | None = None
    minutes_played: int | None = None
    rating: float | None = None
    stats: dict[str, float] = {}


class DomainShot(BaseModel):
    """One shot. Coordinates are 0-100 percentages of the pitch: `x` is the
    distance from the goal being attacked (0 = goal line), `y` the width."""

    source_id: str
    match_source_id: str
    team_source_id: str
    player_source_id: str | None = None
    minute: int
    added_time: int | None = None
    x: float
    y: float
    shot_type: str  # goal / save / miss / block / post
    situation: str | None = None  # regular / corner / free-kick / ...
    body_part: str | None = None
    goal_mouth_location: str | None = None
    xg: float | None = None
    xgot: float | None = None


class DomainMomentum(BaseModel):
    """Attacking-pressure curve: (minute, value) with value > 0 when the
    home team dominates and < 0 when the away team does."""

    match_source_id: str
    points: list[tuple[float, int]]


class DomainTeamHeatmap(BaseModel):
    """Outfield players' touch positions for one team in one match, 0-100
    coordinates with the team attacking toward x = 100."""

    match_source_id: str
    team_source_id: str
    points: list[tuple[float, float]]


class DomainMatchEvent(BaseModel):
    match_source_id: str
    team_source_id: str
    player_source_id: str | None = None
    related_player_source_id: str | None = None
    event_type: str
    event_detail: str | None = None
    minute: int
    extra_minute: int | None = None
