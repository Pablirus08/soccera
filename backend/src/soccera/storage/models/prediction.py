from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from soccera.storage.models.base import Base, TimestampMixin


class Prediction(Base, TimestampMixin):
    """
    One row per model run for a match. Written by Phase 2+ (Poisson/Dixon-Coles,
    Elo, live win probability) — the schema exists now so ingestion and
    modeling can be developed independently.
    """

    __tablename__ = "predictions"
    __table_args__ = (Index("ix_predictions_match_model", "match_id", "model_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_type: Mapped[str] = mapped_column(String(20), nullable=False, default="pre_match")
    # "pre_match" or "live"
    minute: Mapped[int | None] = mapped_column(Integer)
    # elapsed minute the live prediction was generated at; null for pre_match

    home_win_prob: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    draw_prob: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    away_win_prob: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    expected_home_goals: Mapped[float | None] = mapped_column(Numeric(5, 2))
    expected_away_goals: Mapped[float | None] = mapped_column(Numeric(5, 2))

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    prediction_metadata: Mapped[dict | None] = mapped_column(JSON)

    match: Mapped["Match"] = relationship(back_populates="predictions")
