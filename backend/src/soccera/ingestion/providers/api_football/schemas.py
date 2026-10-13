"""
Pydantic models mirroring API-Football v3's actual JSON response shapes.
These are intentionally separate from ingestion.domain — this module is
allowed to change whenever API-Football changes its contract; the domain
models it gets mapped to (in mappers.py) must not.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class RawVenue(BaseModel):
    id: int | None = None
    name: str | None = None
    city: str | None = None
    capacity: int | None = None


class RawLeagueInfo(BaseModel):
    id: int
    name: str
    country: str | None = None
    type: str | None = "League"


class RawSeasonInfo(BaseModel):
    year: int
    start: str | None = None
    end: str | None = None
    current: bool = False


class RawLeagueEntry(BaseModel):
    league: RawLeagueInfo
    country: dict | None = None
    seasons: list[RawSeasonInfo] = Field(default_factory=list)


class RawTeamInfo(BaseModel):
    id: int
    name: str
    code: str | None = None
    country: str | None = None
    founded: int | None = None


class RawTeamEntry(BaseModel):
    team: RawTeamInfo
    venue: RawVenue | None = None


class RawPlayerBirth(BaseModel):
    date: str | None = None


class RawPlayerInfo(BaseModel):
    id: int
    name: str
    firstname: str | None = None
    lastname: str | None = None
    nationality: str | None = None
    birth: RawPlayerBirth | None = None


class RawPlayerStatisticsGames(BaseModel):
    position: str | None = None
    number: int | None = None


class RawPlayerStatistics(BaseModel):
    games: RawPlayerStatisticsGames | None = None


class RawPlayerEntry(BaseModel):
    player: RawPlayerInfo
    statistics: list[RawPlayerStatistics] = Field(default_factory=list)


class RawFixtureStatus(BaseModel):
    short: str
    elapsed: int | None = None


class RawFixtureInfo(BaseModel):
    id: int
    referee: str | None = None
    date: datetime
    venue: RawVenue | None = None
    status: RawFixtureStatus


class RawFixtureLeague(BaseModel):
    id: int
    season: int
    round: str | None = None


class RawFixtureTeamRef(BaseModel):
    id: int


class RawFixtureTeams(BaseModel):
    home: RawFixtureTeamRef
    away: RawFixtureTeamRef


class RawFixtureScore(BaseModel):
    home: int | None = None
    away: int | None = None


class RawFixtureScores(BaseModel):
    halftime: RawFixtureScore


class RawFixtureEntry(BaseModel):
    fixture: RawFixtureInfo
    league: RawFixtureLeague
    teams: RawFixtureTeams
    goals: RawFixtureScore
    score: RawFixtureScores


class RawStatisticValue(BaseModel):
    type: str
    value: float | str | None = None


class RawFixtureStatisticsEntry(BaseModel):
    team: RawFixtureTeamRef
    statistics: list[RawStatisticValue] = Field(default_factory=list)


class RawEventTeam(BaseModel):
    id: int


class RawEventPlayer(BaseModel):
    id: int | None = None


class RawFixtureEventEntry(BaseModel):
    time: dict
    team: RawEventTeam
    player: RawEventPlayer | None = None
    assist: RawEventPlayer | None = None
    type: str
    detail: str | None = None
