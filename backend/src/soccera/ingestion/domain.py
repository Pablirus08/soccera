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


class DomainMatchEvent(BaseModel):
    match_source_id: str
    team_source_id: str
    player_source_id: str | None = None
    related_player_source_id: str | None = None
    event_type: str
    event_detail: str | None = None
    minute: int
    extra_minute: int | None = None
