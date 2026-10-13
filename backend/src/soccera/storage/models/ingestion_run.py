from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from soccera.storage.models.base import Base


class IngestionRun(Base):
    """
    Audit log for ingestion jobs. Not required for correctness, but cheap
    to have from day one and saves a lot of debugging time once historical
    backfills and live polling are both running.
    """

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    job_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # "historical_backfill" or "live_poll"
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # "league" / "season" / "team" / "match" / ...
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="started")
    # "started" / "success" / "failed"
    league_source_id: Mapped[str | None] = mapped_column(String(64))
    season_year: Mapped[int | None] = mapped_column(Integer)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
