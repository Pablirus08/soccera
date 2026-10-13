from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from soccera.storage.models.match_visuals import MatchMomentum, MatchShot, MatchTeamHeatmap


class MatchVisualsRepository:
    """Writes for shots, momentum and heatmaps; each replaces a match's data
    wholesale, like events, since providers resend the full set every time."""

    def __init__(self, session: Session):
        self.session = session

    def replace_shots(self, match_id: int, shots: list[MatchShot]) -> None:
        self.session.execute(delete(MatchShot).where(MatchShot.match_id == match_id))
        self.session.add_all(shots)
        self.session.flush()

    def upsert_momentum(self, match_id: int, points: list[Any]) -> None:
        stmt = select(MatchMomentum).where(MatchMomentum.match_id == match_id)
        instance = self.session.execute(stmt).scalar_one_or_none()
        if instance is None:
            self.session.add(MatchMomentum(match_id=match_id, points=points))
        else:
            instance.points = points
        self.session.flush()

    def upsert_heatmap(self, match_id: int, team_id: int, grid: list[int], points: int) -> None:
        stmt = select(MatchTeamHeatmap).where(
            MatchTeamHeatmap.match_id == match_id, MatchTeamHeatmap.team_id == team_id
        )
        instance = self.session.execute(stmt).scalar_one_or_none()
        if instance is None:
            self.session.add(
                MatchTeamHeatmap(match_id=match_id, team_id=team_id, grid=grid, points=points)
            )
        else:
            instance.grid, instance.points = grid, points
        self.session.flush()

    def match_ids_with_momentum(self, match_ids: list[int]) -> set[int]:
        if not match_ids:
            return set()
        stmt = select(MatchMomentum.match_id).where(MatchMomentum.match_id.in_(match_ids))
        return set(self.session.execute(stmt).scalars())
