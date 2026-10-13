import time

from soccera.config import get_settings
from soccera.ingestion.base import DataSourceAdapter
from soccera.ingestion.sync.pipeline import sync_fixture_details, sync_live_fixtures
from soccera.logging import get_logger
from soccera.storage.database import session_scope
from soccera.storage.models.match import Match
from soccera.storage.repositories import IngestionRunRepository, MatchRepository

logger = get_logger(__name__)


def run_live_poll_once(adapter: DataSourceAdapter) -> int:
    """
    One polling cycle: upsert whatever is currently live, then pull fresh
    events/statistics for each of those matches. Returns the number of
    live matches processed.
    """
    with session_scope() as session:
        run_repo = IngestionRunRepository(session)
        run = run_repo.start(adapter.source_name, "live_poll", "fixtures")
        try:
            sync_live_fixtures(adapter, session)
            live_matches: list[Match] = MatchRepository(session).get_live()
            for match in live_matches:
                sync_fixture_details(adapter, session, match.source_id)
            run_repo.finish(run, records_processed=len(live_matches))
            logger.info("sync.live_poll_complete", live_matches=len(live_matches))
            return len(live_matches)
        except Exception as exc:
            run_repo.finish(run, records_processed=0, error_message=str(exc))
            session.commit()
            logger.error("sync.live_poll_failed", error=str(exc))
            raise


def run_live_poll_forever(adapter: DataSourceAdapter) -> None:
    """Blocking loop for the ingestion service's live-polling process."""
    interval = get_settings().live_poll_interval_seconds
    while True:
        try:
            run_live_poll_once(adapter)
        except Exception:
            # Logged with full context in run_live_poll_once; keep polling
            # rather than let one bad cycle kill the whole process.
            pass
        time.sleep(interval)
