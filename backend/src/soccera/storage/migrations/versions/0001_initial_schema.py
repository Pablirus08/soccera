"""initial schema: leagues, seasons, venues, teams, players, matches, events, predictions

Revision ID: 0001
Revises:
Create Date: 2026-08-10

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MATCH_STATUSES = (
    "SCHEDULED",
    "LIVE",
    "HALFTIME",
    "FINISHED",
    "POSTPONED",
    "CANCELLED",
    "SUSPENDED",
)


def upgrade() -> None:
    op.create_table(
        "venues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="api_football"),
        sa.Column("source_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("city", sa.String(120)),
        sa.Column("country", sa.String(120)),
        sa.Column("capacity", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source", "source_id", name="uq_venues_source"),
    )

    op.create_table(
        "leagues",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="api_football"),
        sa.Column("source_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("country", sa.String(120)),
        sa.Column("type", sa.String(20), nullable=False, server_default="league"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source", "source_id", name="uq_leagues_source"),
    )

    op.create_table(
        "seasons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("league_id", sa.Integer(), sa.ForeignKey("leagues.id"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("league_id", "year", name="uq_seasons_league_year"),
    )

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="api_football"),
        sa.Column("source_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("short_name", sa.String(50)),
        sa.Column("country", sa.String(120)),
        sa.Column("founded", sa.Integer()),
        sa.Column("venue_id", sa.Integer(), sa.ForeignKey("venues.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source", "source_id", name="uq_teams_source"),
    )

    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="api_football"),
        sa.Column("source_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("first_name", sa.String(120)),
        sa.Column("last_name", sa.String(120)),
        sa.Column("birth_date", sa.Date()),
        sa.Column("nationality", sa.String(120)),
        sa.Column("position", sa.String(20)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source", "source_id", name="uq_players_source"),
    )

    op.create_table(
        "team_players",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("shirt_number", sa.Integer()),
        sa.Column("position", sa.String(20)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("team_id", "player_id", "season_id", name="uq_team_players_roster"),
    )
    op.create_index("ix_team_players_team_season", "team_players", ["team_id", "season_id"])

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="api_football"),
        sa.Column("source_id", sa.String(64), nullable=False),
        sa.Column("league_id", sa.Integer(), sa.ForeignKey("leagues.id"), nullable=False),
        sa.Column("season_id", sa.Integer(), sa.ForeignKey("seasons.id"), nullable=False),
        sa.Column("home_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("away_team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("venue_id", sa.Integer(), sa.ForeignKey("venues.id")),
        sa.Column("match_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="SCHEDULED"),
        sa.Column("elapsed_minutes", sa.Integer()),
        sa.Column("round", sa.String(100)),
        sa.Column("referee", sa.String(150)),
        sa.Column("home_score", sa.Integer()),
        sa.Column("away_score", sa.Integer()),
        sa.Column("home_score_ht", sa.Integer()),
        sa.Column("away_score_ht", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source", "source_id", name="uq_matches_source"),
        sa.CheckConstraint(f"status IN {MATCH_STATUSES}", name="ck_matches_status"),
    )
    op.create_index("ix_matches_league_season", "matches", ["league_id", "season_id"])
    op.create_index("ix_matches_match_date", "matches", ["match_date"])
    op.create_index(
        "ix_matches_live_status",
        "matches",
        ["status"],
        postgresql_where=sa.text("status = 'LIVE'"),
    )

    op.create_table(
        "match_statistics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("stat_type", sa.String(50), nullable=False),
        sa.Column("stat_value", sa.Numeric(10, 2)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint(
            "match_id", "team_id", "stat_type", name="uq_match_statistics_match_team_stat"
        ),
    )

    op.create_table(
        "match_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("team_id", sa.Integer(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("player_id", sa.Integer(), sa.ForeignKey("players.id")),
        sa.Column("related_player_id", sa.Integer(), sa.ForeignKey("players.id")),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("event_detail", sa.String(100)),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("extra_minute", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_match_events_match_id", "match_events", ["match_id"])

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("match_id", sa.Integer(), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("prediction_type", sa.String(20), nullable=False, server_default="pre_match"),
        sa.Column("minute", sa.Integer()),
        sa.Column("home_win_prob", sa.Numeric(5, 4), nullable=False),
        sa.Column("draw_prob", sa.Numeric(5, 4), nullable=False),
        sa.Column("away_win_prob", sa.Numeric(5, 4), nullable=False),
        sa.Column("expected_home_goals", sa.Numeric(5, 2)),
        sa.Column("expected_away_goals", sa.Numeric(5, 2)),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("prediction_metadata", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_predictions_match_model", "predictions", ["match_id", "model_name"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("job_type", sa.String(30), nullable=False),
        sa.Column("entity_type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="started"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("records_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
    )


def downgrade() -> None:
    op.drop_table("ingestion_runs")
    op.drop_index("ix_predictions_match_model", table_name="predictions")
    op.drop_table("predictions")
    op.drop_index("ix_match_events_match_id", table_name="match_events")
    op.drop_table("match_events")
    op.drop_table("match_statistics")
    op.drop_index("ix_matches_live_status", table_name="matches")
    op.drop_index("ix_matches_match_date", table_name="matches")
    op.drop_index("ix_matches_league_season", table_name="matches")
    op.drop_table("matches")
    op.drop_index("ix_team_players_team_season", table_name="team_players")
    op.drop_table("team_players")
    op.drop_table("players")
    op.drop_table("teams")
    op.drop_table("seasons")
    op.drop_table("leagues")
    op.drop_table("venues")
