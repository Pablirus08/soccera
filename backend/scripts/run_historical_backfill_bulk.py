"""
Backfills fixtures (leagues/seasons/teams/matches, no events/statistics yet)
for every Costa Rica Primera Division season in a year range, across both
tournaments (Apertura + Clausura). Safe to re-run — each season is
idempotent, and a season that fails or doesn't exist on Sofascore is
skipped without stopping the rest.

Usage: python scripts/run_historical_backfill_bulk.py [from_year] [to_year]
  Defaults to 2022..current year.
"""

import sys
from datetime import datetime

from soccera.ingestion.providers.costa_rica.adapter import SofascoreAdapter
from soccera.ingestion.sync.historical import run_historical_backfill
from soccera.logging import configure_logging, get_logger

logger = get_logger(__name__)

LEAGUES = {"11535": "Apertura", "11542": "Clausura"}


def main() -> None:
    configure_logging()
    from_year = int(sys.argv[1]) if len(sys.argv) > 1 else 2022
    to_year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year

    adapter = SofascoreAdapter()
    results: list[tuple[str, int, str]] = []
    try:
        for league_id, label in LEAGUES.items():
            for year in range(from_year, to_year + 1):
                tag = f"{label} {year} (league {league_id})"
                try:
                    count = run_historical_backfill(adapter, league_id, year)
                    status = f"{count} fixtures"
                    print(f"[OK]   {tag}: {status}")
                except Exception as exc:
                    status = f"SKIPPED: {exc}"
                    print(f"[SKIP] {tag}: {exc}")
                results.append((tag, year, status))
    finally:
        adapter.close()

    print("\nSummary:")
    for tag, _year, status in results:
        print(f"  {tag}: {status}")


if __name__ == "__main__":
    main()
