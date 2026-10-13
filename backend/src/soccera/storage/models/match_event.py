from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soccera.storage.models.base import Base, TimestampMixin


class MatchEvent(Base, TimestampMixin):
    __tablename__ = "match_events"
    __table_args__ = (Index("ix_match_events_match_id", "match_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))
    related_player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))
    # e.g. assist provider for a goal, or player subbed off for a substitution

    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # GOAL / CARD / SUBSTITUTION / VAR
    event_detail: Mapped[str | None] = mapped_column(String(100))
    # e.g. "Normal Goal", "Yellow Card", "Red Card", "Penalty"
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    extra_minute: Mapped[int | None] = mapped_column(Integer)

    match: Mapped["Match"] = relationship(back_populates="events")
    team: Mapped["Team"] = relationship()
