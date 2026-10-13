"""match_player_stats: per-player stat line for each match

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-13

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "match_player_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("is_starter", sa.Boolean(), nullable=False),
        sa.Column("shirt_number", sa.Integer()),
        sa.Column("position", sa.String(20)),
        sa.Column("minutes_played", sa.Integer()),
        sa.Column("rating", sa.Numeric(4, 2)),
        sa.Column(
            "stats",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("match_id", "player_id", name="uq_match_player_stats_match_player"),
    )
    op.create_index("ix_match_player_stats_player", "match_player_stats", ["player_id"])


def downgrade() -> None:
    op.drop_index("ix_match_player_stats_player", table_name="match_player_stats")
    op.drop_table("match_player_stats")
