"""
Usage: python scripts/run_backfill.py <league_source_id> <season_year> [from] [to]
Dates are ISO format (YYYY-MM-DD). Example:
  python scripts/run_backfill.py 71 2024 2024-01-01 2024-12-31   # Brazil Serie A, 2024
"""

import sys
from datetime import date

from soccera.ingestion.providers.api_football.adapter import ApiFootballAdapter
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

    adapter = ApiFootballAdapter()
    try:
        count = run_historical_backfill(adapter, league_source_id, season_year, date_from, date_to)
        print(f"Synced {count} fixtures for league {league_source_id}, season {season_year}")
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
