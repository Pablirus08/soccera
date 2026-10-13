from datetime import date

from soccera.ingestion.base import DataSourceAdapter
from soccera.ingestion.sync.pipeline import sync_fixtures, sync_leagues, sync_teams
from soccera.logging import get_logger
from soccera.storage.database import session_scope
from soccera.storage.repositories import IngestionRunRepository

logger = get_logger(__name__)


def run_historical_backfill(
    adapter: DataSourceAdapter,
    league_source_id: str,
    season_year: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> int:
    """
    Backfills a single league+season: leagues/seasons, then teams, then
    fixtures. Each step is idempotent, so re-running this after a partial
    failure is safe.
    """
    with session_scope() as session:
        run_repo = IngestionRunRepository(session)
        run = run_repo.start(
            adapter.source_name,
            "historical_backfill",
            "fixtures",
            league_source_id=league_source_id,
            season_year=season_year,
        )
        try:
            sync_leagues(adapter, session)
            sync_teams(adapter, session, league_source_id, season_year)
            fixture_count = sync_fixtures(
                adapter, session, league_source_id, season_year, date_from, date_to
            )
            run_repo.finish(run, records_processed=fixture_count)
            logger.info(
                "sync.historical_backfill_complete",
                league_source_id=league_source_id,
                season_year=season_year,
                fixtures_synced=fixture_count,
            )
            return fixture_count
        except Exception as exc:
            # Commit the failure record now — session_scope will roll back
            # the enclosing transaction on the way out, which would
            # otherwise discard this audit row along with everything else.
            run_repo.finish(run, records_processed=0, error_message=str(exc))
            session.commit()
            logger.error(
                "sync.historical_backfill_failed",
                league_source_id=league_source_id,
                season_year=season_year,
                error=str(exc),
            )
            raise
