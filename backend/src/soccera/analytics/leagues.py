from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.storage.models.league import League


@dataclass
class SeasonOption:
    year: int
    is_current: bool


@dataclass
class LeagueOption:
    source: str
    source_id: str
    name: str
    country: str | None
    seasons: list[SeasonOption] = field(default_factory=list)


def list_leagues(session: Session) -> list[LeagueOption]:
    leagues = session.execute(select(League)).scalars().all()
    return [
        LeagueOption(
            source=lg.source,
            source_id=lg.source_id,
            name=lg.name,
            country=lg.country,
            seasons=sorted(
                (SeasonOption(year=s.year, is_current=s.is_current) for s in lg.seasons),
                key=lambda s: -s.year,
            ),
        )
        for lg in leagues
    ]
