"""
Read-only exploration script — hits API-Football and prints results to the
terminal. Nothing gets written to the database; use this to see what a
league/season/fixture actually looks like before deciding what to store.

Usage:
  python scripts/explore_api.py seasons <league_id>
  python scripts/explore_api.py teams <league_id> <season_year>
  python scripts/explore_api.py fixtures <league_id> <season_year> [from] [to]
  python scripts/explore_api.py fixture-detail <fixture_id>

Example (Costa Rica Primera Division, league 162):
  python scripts/explore_api.py seasons 162
  python scripts/explore_api.py fixtures 162 2025
"""

import sys
from datetime import date

from soccera.ingestion.providers.api_football.adapter import ApiFootballAdapter


def print_seasons(adapter: ApiFootballAdapter, league_id: str) -> None:
    seasons = adapter.get_seasons(league_id)
    if not seasons:
        print(f"No seasons found for league {league_id}")
        return
    for s in seasons:
        marker = " <- current" if s.is_current else ""
        print(f"  year={s.year}  {s.start_date} to {s.end_date}{marker}")


def print_teams(adapter: ApiFootballAdapter, league_id: str, season_year: int) -> None:
    teams = adapter.get_teams(league_id, season_year)
    if not teams:
        print(f"No teams found for league {league_id}, season {season_year}")
        return
    for t in teams:
        venue = f" @ {t.venue.name}" if t.venue else ""
        print(f"  id={t.source_id}  {t.name} ({t.short_name}){venue}")


def print_fixtures(
    adapter: ApiFootballAdapter,
    league_id: str,
    season_year: int,
    date_from: date | None,
    date_to: date | None,
) -> None:
    fixtures = adapter.get_fixtures(league_id, season_year, date_from, date_to)
    if not fixtures:
        print(f"No fixtures found for league {league_id}, season {season_year}")
        return
    for f in fixtures:
        score = (
            f"{f.home_score}-{f.away_score}"
            if f.home_score is not None
            else "vs"
        )
        print(
            f"  id={f.source_id}  {f.match_date:%Y-%m-%d %H:%M}  "
            f"{f.home_team_source_id} {score} {f.away_team_source_id}  "
            f"[{f.status}]  round={f.round}"
        )
    print(f"\n{len(fixtures)} fixtures total")


def print_fixture_detail(adapter: ApiFootballAdapter, fixture_id: str) -> None:
    events = adapter.get_fixture_events(fixture_id)
    stats = adapter.get_fixture_statistics(fixture_id)

    print(f"Events ({len(events)}):")
    for e in events:
        detail = f" ({e.event_detail})" if e.event_detail else ""
        print(f"  {e.minute}' team={e.team_source_id} {e.event_type}{detail}")

    print(f"\nStatistics ({len(stats)}):")
    for s in stats:
        print(f"  team={s.team_source_id}  {s.stat_type}: {s.stat_value}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    adapter = ApiFootballAdapter()
    try:
        if command == "seasons":
            print_seasons(adapter, sys.argv[2])
        elif command == "teams":
            print_teams(adapter, sys.argv[2], int(sys.argv[3]))
        elif command == "fixtures":
            date_from = date.fromisoformat(sys.argv[4]) if len(sys.argv) > 4 else None
            date_to = date.fromisoformat(sys.argv[5]) if len(sys.argv) > 5 else None
            print_fixtures(adapter, sys.argv[2], int(sys.argv[3]), date_from, date_to)
        elif command == "fixture-detail":
            print_fixture_detail(adapter, sys.argv[2])
        else:
            print(f"Unknown command: {command}\n")
            print(__doc__)
            sys.exit(1)
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
