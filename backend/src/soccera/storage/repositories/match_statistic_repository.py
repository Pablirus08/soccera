from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.storage.models.match_statistic import MatchStatistic


class MatchStatisticRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert(
        self, match_id: int, team_id: int, stat_type: str, stat_value: float | None
    ) -> MatchStatistic:
        stmt = select(MatchStatistic).where(
            MatchStatistic.match_id == match_id,
            MatchStatistic.team_id == team_id,
            MatchStatistic.stat_type == stat_type,
        )
        instance = self.session.execute(stmt).scalar_one_or_none()
        if instance is None:
            instance = MatchStatistic(
                match_id=match_id, team_id=team_id, stat_type=stat_type, stat_value=stat_value
            )
            self.session.add(instance)
        else:
            instance.stat_value = stat_value
        self.session.flush()
        return instance
