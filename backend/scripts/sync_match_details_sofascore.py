"""
Fills in events + statistics for already-synced Sofascore matches of a
league/season (run_backfill_sofascore.py only syncs the fixture list
itself — this fetches the per-match detail on top of it).

Each match costs a few Sofascore browser calls, so this can take a while
for a full season; it's safe to re-run (idempotent upserts).

Usage: python scripts/sync_match_details_sofascore.py <league_id> <season_year> [--finished-only]
"""

import sys

from soccera.ingestion.providers.costa_rica.adapter import SofascoreAdapter
from soccera.ingestion.sync.pipeline import sync_fixture_details
from soccera.logging import configure_logging, get_logger
from soccera.storage.database import session_scope
from soccera.storage.repositories import LeagueRepository, MatchRepository, SeasonRepository

logger = get_logger(__name__)


def main() -> None:
    configure_logging()
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    league_source_id = sys.argv[1]
    season_year = int(sys.argv[2])
    finished_only = "--finished-only" in sys.argv

    adapter = SofascoreAdapter()
    try:
        with session_scope() as session:
            league = LeagueRepository(session).get_by_source(adapter.source_name, league_source_id)
            if league is None:
                print(f"League {league_source_id} not synced yet — run run_backfill_sofascore.py first")
                sys.exit(1)
            season = SeasonRepository(session).get_by_league_and_year(league.id, season_year)
            if season is None:
                print(f"Season {season_year} not synced yet — run run_backfill_sofascore.py first")
                sys.exit(1)

            matches = MatchRepository(session).get_by_league_and_season(league.id, season.id)
            if finished_only:
                matches = [m for m in matches if m.status == "FINISHED"]

            print(f"Syncing details for {len(matches)} matches...")
            for i, match in enumerate(matches, 1):
                sync_fixture_details(adapter, session, match.source_id)
                print(f"  [{i}/{len(matches)}] match {match.source_id} done")
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
