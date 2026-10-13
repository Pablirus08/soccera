from datetime import datetime

from sqlalchemy import select

from soccera.storage.models.match import Match
from soccera.storage.repositories.base import SourceKeyedRepository


class MatchRepository(SourceKeyedRepository[Match]):
    model = Match

    def get_live(self) -> list[Match]:
        stmt = select(Match).where(Match.status == "LIVE")
        return list(self.session.execute(stmt).scalars())

    def get_by_date_range(self, start: datetime, end: datetime) -> list[Match]:
        stmt = select(Match).where(Match.match_date >= start, Match.match_date < end)
        return list(self.session.execute(stmt).scalars())

    def get_finished(self, source: str, before: datetime | None = None) -> list[Match]:
        stmt = (
            select(Match)
            .where(Match.source == source, Match.status == "FINISHED")
            .order_by(Match.match_date)
        )
        if before is not None:
            stmt = stmt.where(Match.match_date < before)
        return list(self.session.execute(stmt).scalars())

    def get_scheduled(self, source: str) -> list[Match]:
        stmt = (
            select(Match)
            .where(Match.source == source, Match.status == "SCHEDULED")
            .order_by(Match.match_date)
        )
        return list(self.session.execute(stmt).scalars())

    def get_by_league_and_season(self, league_id: int, season_id: int) -> list[Match]:
        stmt = select(Match).where(Match.league_id == league_id, Match.season_id == season_id)
        return list(self.session.execute(stmt).scalars())
