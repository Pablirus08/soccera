"""
"Bring this league/season up to date", as triggered by the frontend's
update button: a database-only freshness check, plus a sync that only hits
the provider for what is actually stale.
"""

import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.analytics.common import get_league_and_season
from soccera.ingestion.base import DataSourceAdapter
from soccera.ingestion.sync.historical import run_historical_backfill
from soccera.ingestion.sync.pipeline import needs_details, sync_fixture_details
from soccera.logging import get_logger
from soccera.storage.database import session_scope
from soccera.storage.models.ingestion_run import IngestionRun
from soccera.storage.repositories import MatchRepository

logger = get_logger(__name__)

# Statuses that mean "the provider will have newer data once kickoff has passed".
_OPEN_STATUSES = ("SCHEDULED", "LIVE", "HALFTIME")

# Caps provider traffic per sync request; anything beyond is reported as pending.
MAX_DETAIL_MATCHES_PER_SYNC = 15
PAUSE_BETWEEN_MATCHES_SECONDS = 1.0

_sync_lock = threading.Lock()


class SyncInProgressError(RuntimeError):
    pass


@dataclass
class SyncStatus:
    up_to_date: bool
    overdue_matches: int  # kicked off but not stored as finished yet
    details_pending: int  # finished but missing (or stale) detail
    last_synced_at: datetime | None
    last_match_date: datetime | None
    next_match_date: datetime | None


@dataclass
class SyncResult:
    fixtures_synced: int
    details_synced: int
    status: SyncStatus


def check_sync_status(
    session: Session, source: str, league_source_id: str, season_year: int
) -> SyncStatus:
    """Answers "is anything newer available?" from the database alone."""
    league, season = get_league_and_season(session, source, league_source_id, season_year)
    matches = MatchRepository(session).get_by_league_and_season(league.id, season.id)
    now = datetime.now(UTC)

    overdue = [m for m in matches if m.status in _OPEN_STATUSES and m.match_date <= now]
    pending = [m for m in matches if needs_details(m)]
    finished = [m.match_date for m in matches if m.status == "FINISHED"]
    upcoming = [m.match_date for m in matches if m.status == "SCHEDULED" and m.match_date > now]

    last_run = session.execute(
        select(IngestionRun.finished_at)
        .where(
            IngestionRun.source == source,
            IngestionRun.league_source_id == league_source_id,
            IngestionRun.season_year == season_year,
            IngestionRun.status == "success",
        )
        .order_by(IngestionRun.finished_at.desc())
        .limit(1)
    ).scalar_one_or_none()

    return SyncStatus(
        up_to_date=bool(matches) and not overdue and not pending,
        overdue_matches=len(overdue),
        details_pending=len(pending),
        last_synced_at=last_run,
        last_match_date=max(finished, default=None),
        next_match_date=min(upcoming, default=None),
    )


def sync_season(
    adapter: DataSourceAdapter,
    league_source_id: str,
    season_year: int,
    max_detail_matches: int = MAX_DETAIL_MATCHES_PER_SYNC,
) -> SyncResult:
    """
    Refreshes the fixture list (scores, statuses, upcoming games), then
    fetches detail for up to `max_detail_matches` finished matches that need
    it, oldest first. One sync at a time per process — a second concurrent
    request raises SyncInProgressError instead of doubling provider traffic.
    """
    if not _sync_lock.acquire(blocking=False):
        raise SyncInProgressError("A sync is already running")
    try:
        fixtures_synced = run_historical_backfill(adapter, league_source_id, season_year)

        with session_scope() as session:
            league, season = get_league_and_season(
                session, adapter.source_name, league_source_id, season_year
            )
            matches = MatchRepository(session).get_by_league_and_season(league.id, season.id)
            to_fetch = sorted((m for m in matches if needs_details(m)), key=lambda m: m.match_date)
            source_ids = [m.source_id for m in to_fetch[:max_detail_matches]]

        details_synced = 0
        for i, source_id in enumerate(source_ids):
            if i:
                time.sleep(PAUSE_BETWEEN_MATCHES_SECONDS)
            with session_scope() as session:
                sync_fixture_details(adapter, session, source_id)
            details_synced += 1

        with session_scope() as session:
            status = check_sync_status(session, adapter.source_name, league_source_id, season_year)
        logger.info(
            "sync.season_complete",
            league_source_id=league_source_id,
            season_year=season_year,
            fixtures_synced=fixtures_synced,
            details_synced=details_synced,
            details_pending=status.details_pending,
        )
        return SyncResult(fixtures_synced, details_synced, status)
    finally:
        _sync_lock.release()
