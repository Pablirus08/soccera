"""matches.details_synced_at: when per-match detail was last fetched

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-13

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("details_synced_at", sa.DateTime(timezone=True)))
    # Finished matches that already have events were detail-synced by an
    # earlier run; mark them so the freshness check doesn't refetch them.
    op.execute(
        """
        UPDATE matches SET details_synced_at = now()
        WHERE status = 'FINISHED'
          AND EXISTS (SELECT 1 FROM match_events e WHERE e.match_id = matches.id)
        """
    )


def downgrade() -> None:
    op.drop_column("matches", "details_synced_at")
