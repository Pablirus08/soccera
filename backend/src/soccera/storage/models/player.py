from datetime import date

from sqlalchemy import Date, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from soccera.storage.models.base import Base, SourceMixin, TimestampMixin


class Player(Base, SourceMixin, TimestampMixin):
    __tablename__ = "players"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_players_source"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    birth_date: Mapped[date | None] = mapped_column(Date)
    nationality: Mapped[str | None] = mapped_column(String(120))
    position: Mapped[str | None] = mapped_column(String(20))
    # Goalkeeper / Defender / Midfielder / Attacker
