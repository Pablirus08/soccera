from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soccera.storage.models.base import Base, SourceMixin, TimestampMixin

MATCH_STATUSES = (
    "SCHEDULED",
    "LIVE",
    "HALFTIME",
    "FINISHED",
    "POSTPONED",
    "CANCELLED",
    "SUSPENDED",
)


class Match(Base, SourceMixin, TimestampMixin):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_matches_source"),
        CheckConstraint(f"status IN {MATCH_STATUSES}", name="ck_matches_status"),
        Index("ix_matches_league_season", "league_id", "season_id"),
        Index("ix_matches_match_date", "match_date"),
        Index(
            "ix_matches_live_status",
            "status",
            postgresql_where=text("status = 'LIVE'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id"))

    match_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SCHEDULED")
    elapsed_minutes: Mapped[int | None] = mapped_column(Integer)
    round: Mapped[str | None] = mapped_column(String(100))
    referee: Mapped[str | None] = mapped_column(String(150))

    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)
    home_score_ht: Mapped[int | None] = mapped_column(Integer)
    away_score_ht: Mapped[int | None] = mapped_column(Integer)

    # When events/lineups/statistics were last fetched. Lets "is everything
    # up to date?" be answered from the database without calling the provider.
    details_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    league: Mapped["League"] = relationship()
    season: Mapped["Season"] = relationship(back_populates="matches")
    home_team: Mapped["Team"] = relationship(foreign_keys=[home_team_id])
    away_team: Mapped["Team"] = relationship(foreign_keys=[away_team_id])
    venue: Mapped["Venue"] = relationship()

    events: Mapped[list["MatchEvent"]] = relationship(back_populates="match")
    statistics: Mapped[list["MatchStatistic"]] = relationship(back_populates="match")
    player_stats: Mapped[list["MatchPlayerStat"]] = relationship(back_populates="match")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="match")
