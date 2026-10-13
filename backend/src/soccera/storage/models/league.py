from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soccera.storage.models.base import Base, SourceMixin, TimestampMixin


class League(Base, SourceMixin, TimestampMixin):
    __tablename__ = "leagues"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_leagues_source"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    country: Mapped[str | None] = mapped_column(String(120))
    type: Mapped[str] = mapped_column(String(20), nullable=False, default="league")
    # "league" (round-robin) or "cup" (knockout)

    seasons: Mapped[list["Season"]] = relationship(back_populates="league")
