"""
Spatial and timeline data per match: shots, the momentum curve and team
heatmaps. Kept apart from MatchEvent/MatchStatistic because they're much
bulkier and only some providers have them.
"""

from typing import Any

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soccera.storage.models.base import Base, TimestampMixin

# Heatmaps are stored pre-binned on this grid (pitch ratio ~105x68), so a
# season aggregate is just an element-wise sum of each match's counts.
HEATMAP_COLS = 24  # along the pitch length, team attacking toward the last column
HEATMAP_ROWS = 16  # across the width


class MatchShot(Base, TimestampMixin):
    """x/y are 0-100: x = distance from the goal being attacked, y = width."""

    __tablename__ = "match_shots"
    __table_args__ = (
        UniqueConstraint("match_id", "source_id", name="uq_match_shots_match_source"),
        Index("ix_match_shots_team", "team_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)

    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    added_time: Mapped[int | None] = mapped_column(Integer)
    x: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    y: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    shot_type: Mapped[str] = mapped_column(String(20), nullable=False)
    situation: Mapped[str | None] = mapped_column(String(30))
    body_part: Mapped[str | None] = mapped_column(String(20))
    goal_mouth_location: Mapped[str | None] = mapped_column(String(30))
    xg: Mapped[float | None] = mapped_column(Numeric(6, 4))
    xgot: Mapped[float | None] = mapped_column(Numeric(6, 4))

    player: Mapped["Player | None"] = relationship()


class MatchMomentum(Base, TimestampMixin):
    """`points`: [[minute, value], ...]; value > 0 = home team pressing."""

    __tablename__ = "match_momentum"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False, unique=True)
    points: Mapped[list[Any]] = mapped_column(JSONB, nullable=False)


class MatchTeamHeatmap(Base, TimestampMixin):
    """`grid`: HEATMAP_ROWS x HEATMAP_COLS touch counts, row-major."""

    __tablename__ = "match_team_heatmaps"
    __table_args__ = (
        UniqueConstraint("match_id", "team_id", name="uq_match_team_heatmaps_match_team"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    grid: Mapped[list[int]] = mapped_column(JSONB, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
