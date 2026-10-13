from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soccera.storage.models.base import Base, TimestampMixin


class Season(Base, TimestampMixin):
    __tablename__ = "seasons"
    __table_args__ = (UniqueConstraint("league_id", "year", name="uq_seasons_league_year"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    league: Mapped["League"] = relationship(back_populates="seasons")
    matches: Mapped[list["Match"]] = relationship(back_populates="season")
