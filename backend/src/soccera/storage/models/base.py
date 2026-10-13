from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class TimestampMixin:
    """created_at / updated_at columns, maintained by the database."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SourceMixin:
    """
    Tracks which external provider produced this row (e.g. "api_football",
    "cr_scraper") and that provider's ID for the entity. Combined with a
    per-table UniqueConstraint(source, source_id), this makes re-sync
    idempotent (upsert on source+source_id) without coupling storage to
    any one provider's ID scheme.
    """

    source: Mapped[str] = mapped_column(String(50), nullable=False, default="api_football")
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
