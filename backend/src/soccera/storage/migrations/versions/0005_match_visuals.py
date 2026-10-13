"""match visuals: shots, momentum curve, team heatmaps

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-13

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "match_shots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id")),
        sa.Column("source_id", sa.String(64), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("added_time", sa.Integer()),
        sa.Column("x", sa.Numeric(5, 2), nullable=False),
        sa.Column("y", sa.Numeric(5, 2), nullable=False),
        sa.Column("shot_type", sa.String(20), nullable=False),
        sa.Column("situation", sa.String(30)),
        sa.Column("body_part", sa.String(20)),
        sa.Column("goal_mouth_location", sa.String(30)),
        sa.Column("xg", sa.Numeric(6, 4)),
        sa.Column("xgot", sa.Numeric(6, 4)),
        *_timestamps(),
        sa.UniqueConstraint("match_id", "source_id", name="uq_match_shots_match_source"),
    )
    op.create_index("ix_match_shots_team", "match_shots", ["team_id"])

    op.create_table(
        "match_momentum",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False, unique=True
        ),
        sa.Column("points", postgresql.JSONB(), nullable=False),
        *_timestamps(),
    )

    op.create_table(
        "match_team_heatmaps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("grid", postgresql.JSONB(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("match_id", "team_id", name="uq_match_team_heatmaps_match_team"),
    )


def downgrade() -> None:
    op.drop_table("match_team_heatmaps")
    op.drop_table("match_momentum")
    op.drop_index("ix_match_shots_team", table_name="match_shots")
    op.drop_table("match_shots")
