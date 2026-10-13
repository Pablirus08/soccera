from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from soccera.storage.models.base import Base, SourceMixin, TimestampMixin


class Venue(Base, SourceMixin, TimestampMixin):
    __tablename__ = "venues"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_venues_source"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str | None] = mapped_column(String(120))
    country: Mapped[str | None] = mapped_column(String(120))
    capacity: Mapped[int | None] = mapped_column(Integer)
