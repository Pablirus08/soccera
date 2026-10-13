"""
Pydantic models mirroring the subset of Sofascore's JSON response shapes we
actually use. Sofascore's real payloads carry a lot more (translations,
market values, etc.) — pydantic silently ignores unknown fields, so these
only declare what mappers.py needs.
"""

from pydantic import BaseModel


class RawTeamRef(BaseModel):
    id: int
    name: str
    nameCode: str | None = None


class RawScore(BaseModel):
    current: int | None = None
    period1: int | None = None


class RawStatus(BaseModel):
    type: str
    description: str | None = None


class RawRoundInfo(BaseModel):
    round: int | None = None
    name: str | None = None


class RawEventEntry(BaseModel):
    id: int
    startTimestamp: int
    homeTeam: RawTeamRef
    awayTeam: RawTeamRef
    homeScore: RawScore = RawScore()
    awayScore: RawScore = RawScore()
    status: RawStatus
    roundInfo: RawRoundInfo | None = None


class RawIncidentPlayer(BaseModel):
    id: int
    name: str


class RawIncidentEntry(BaseModel):
    incidentType: str
    incidentClass: str | None = None
    time: int | None = None
    addedTime: int | None = None
    isHome: bool | None = None
    player: RawIncidentPlayer | None = None
    playerIn: RawIncidentPlayer | None = None
    playerOut: RawIncidentPlayer | None = None
    assist1: RawIncidentPlayer | None = None


class RawStatisticItem(BaseModel):
    key: str
    name: str
    homeValue: float | None = None
    awayValue: float | None = None


class RawStatisticGroup(BaseModel):
    groupName: str
    statisticsItems: list[RawStatisticItem] = []


class RawStatisticPeriod(BaseModel):
    period: str
    groups: list[RawStatisticGroup] = []


class RawCountry(BaseModel):
    name: str | None = None


class RawSquadPlayer(BaseModel):
    id: int
    name: str
    firstName: str | None = None
    lastName: str | None = None
    position: str | None = None
    jerseyNumber: str | None = None
    dateOfBirthTimestamp: int | None = None
    country: RawCountry | None = None


class RawLineupPlayer(BaseModel):
    """An entry of /event/{id}/lineups -> home|away.players. `statistics` is
    absent for unused substitutes and otherwise mixes numbers with a few
    nested objects (ratingVersions, statisticsType) that the mapper drops."""

    player: RawSquadPlayer
    teamId: int | None = None
    shirtNumber: int | None = None
    position: str | None = None
    substitute: bool = False
    statistics: dict[str, object] = {}


class RawLineupSide(BaseModel):
    players: list[RawLineupPlayer] = []
