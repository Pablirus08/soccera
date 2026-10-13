from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.storage.models.match_player_stat import MatchPlayerStat


class MatchPlayerStatRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert(self, match_id: int, player_id: int, **fields: Any) -> MatchPlayerStat:
        stmt = select(MatchPlayerStat).where(
            MatchPlayerStat.match_id == match_id, MatchPlayerStat.player_id == player_id
        )
        instance = self.session.execute(stmt).scalar_one_or_none()
        if instance is None:
            instance = MatchPlayerStat(match_id=match_id, player_id=player_id, **fields)
            self.session.add(instance)
        else:
            for key, value in fields.items():
                setattr(instance, key, value)
        self.session.flush()
        return instance
