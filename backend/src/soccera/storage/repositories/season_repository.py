from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.storage.models.season import Season


class SeasonRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_league_and_year(self, league_id: int, year: int) -> Season | None:
        stmt = select(Season).where(Season.league_id == league_id, Season.year == year)
        return self.session.execute(stmt).scalar_one_or_none()

    def upsert(self, league_id: int, year: int, **fields: Any) -> Season:
        instance = self.get_by_league_and_year(league_id, year)
        if instance is None:
            instance = Season(league_id=league_id, year=year, **fields)
            self.session.add(instance)
        else:
            for key, value in fields.items():
                setattr(instance, key, value)
        self.session.flush()
        return instance
