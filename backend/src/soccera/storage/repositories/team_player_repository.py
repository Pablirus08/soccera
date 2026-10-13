from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.storage.models.team_player import TeamPlayer


class TeamPlayerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, team_id: int, player_id: int, season_id: int) -> TeamPlayer | None:
        stmt = select(TeamPlayer).where(
            TeamPlayer.team_id == team_id,
            TeamPlayer.player_id == player_id,
            TeamPlayer.season_id == season_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def upsert(self, team_id: int, player_id: int, season_id: int, **fields: Any) -> TeamPlayer:
        instance = self.get(team_id, player_id, season_id)
        if instance is None:
            instance = TeamPlayer(
                team_id=team_id, player_id=player_id, season_id=season_id, **fields
            )
            self.session.add(instance)
        else:
            for key, value in fields.items():
                setattr(instance, key, value)
        self.session.flush()
        return instance
