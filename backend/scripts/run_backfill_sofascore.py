"""
Backfill for Costa Rica's Primera Division via Sofascore — reaches the
current season, unlike API-Football's free plan.

Usage: python scripts/run_backfill_sofascore.py <league_id> <season_year> [from] [to]
  league_id: 11535 (Apertura) or 11542 (Clausura)
  season_year: the year the tournament started, e.g. 2026 for "26/27"

Example (current Apertura season):
  python scripts/run_backfill_sofascore.py 11535 2026
"""

import sys
from datetime import date

from soccera.ingestion.providers.costa_rica.adapter import SofascoreAdapter
from soccera.ingestion.sync.historical import run_historical_backfill
from soccera.logging import configure_logging


def main() -> None:
    configure_logging()
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    league_source_id = sys.argv[1]
    season_year = int(sys.argv[2])
    date_from = date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else None
    date_to = date.fromisoformat(sys.argv[4]) if len(sys.argv) > 4 else None

    adapter = SofascoreAdapter()
    try:
        count = run_historical_backfill(adapter, league_source_id, season_year, date_from, date_to)
        print(f"Synced {count} fixtures for league {league_source_id}, season {season_year}")
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
