"""ingestion_runs: track league_source_id/season_year per run

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-31

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("ingestion_runs", sa.Column("league_source_id", sa.String(64)))
    op.add_column("ingestion_runs", sa.Column("season_year", sa.Integer()))
    op.create_index(
        "ix_ingestion_runs_league_season",
        "ingestion_runs",
        ["source", "league_source_id", "season_year"],
    )


def downgrade() -> None:
    op.drop_index("ix_ingestion_runs_league_season", table_name="ingestion_runs")
    op.drop_column("ingestion_runs", "season_year")
    op.drop_column("ingestion_runs", "league_source_id")
