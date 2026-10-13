from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soccera.storage.models.base import Base, SourceMixin, TimestampMixin


class Team(Base, SourceMixin, TimestampMixin):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_teams_source"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(50))
    country: Mapped[str | None] = mapped_column(String(120))
    founded: Mapped[int | None] = mapped_column(Integer)
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id"))

    venue: Mapped["Venue"] = relationship()
