from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soccera.storage.models.base import Base, TimestampMixin


class MatchStatistic(Base, TimestampMixin):
    """
    Key-value statistic rows (shots_on_goal, possession_pct, corners, ...)
    per team per match. API-Football's stat list varies by competition and
    grows over time; this shape absorbs new stat types with no migration.
    Analytical queries pivot these rows at query time.
    """

    __tablename__ = "match_statistics"
    __table_args__ = (
        UniqueConstraint(
            "match_id", "team_id", "stat_type", name="uq_match_statistics_match_team_stat"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    stat_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # e.g. "shots_on_goal", "possession_pct", "corners", "fouls", "yellow_cards"
    stat_value: Mapped[float | None] = mapped_column(Numeric(10, 2))

    match: Mapped["Match"] = relationship(back_populates="statistics")
    team: Mapped["Team"] = relationship()
