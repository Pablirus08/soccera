from typing import Any

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soccera.storage.models.base import Base, TimestampMixin


class MatchPlayerStat(Base, TimestampMixin):
    """
    One row per player per match they appeared in (starter or used sub).
    minutes_played and rating get real columns because rankings filter and
    sort on them; the long tail of stats (passes, saves, expected_goals, ...)
    lives in `stats` JSONB — providers report different sets, and new keys
    shouldn't need a migration. Query them as stats->>'goals'.
    """

    __tablename__ = "match_player_stats"
    __table_args__ = (
        UniqueConstraint("match_id", "player_id", name="uq_match_player_stats_match_player"),
        Index("ix_match_player_stats_player", "player_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)

    is_starter: Mapped[bool] = mapped_column(Boolean, nullable=False)
    shirt_number: Mapped[int | None] = mapped_column(Integer)
    position: Mapped[str | None] = mapped_column(String(20))
    minutes_played: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[float | None] = mapped_column(Numeric(4, 2))
    stats: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    match: Mapped["Match"] = relationship(back_populates="player_stats")
    team: Mapped["Team"] = relationship()
    player: Mapped["Player"] = relationship()
