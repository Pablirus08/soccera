"""
Fills in lineups + player stats, events, team statistics, shots, momentum
and heatmaps for already-synced Sofascore matches of a league/season
(run_backfill_sofascore.py only syncs the fixture list itself).

Each match costs ~8 Sofascore calls, so it runs in batches: --limit caps how
many matches one run processes and --only-missing skips matches whose detail
is already up to date. --visuals-only fetches just shots/momentum/heatmaps
(~5 calls) for finished matches that don't have them yet. Every match commits
on its own, so an interrupted run keeps its progress. A 403 (blocked) stops
the run immediately rather than hammering the API.

Usage:
  python scripts/sync_match_details_sofascore.py <league_id> <season_year>
      [--finished-only] [--only-missing | --visuals-only] [--limit N] [--pause SECONDS]

Example (current Apertura, next 20 matches still missing detail):
python scripts/sync_match_details_sofascore.py 11535 2026 --finished-only --only-missing --limit 20
"""

import argparse
import sys
import time

from soccera.ingestion.providers.costa_rica.adapter import SofascoreAdapter
from soccera.ingestion.providers.costa_rica.client import SofascoreError
from soccera.ingestion.sync.pipeline import (
    needs_details,
    sync_fixture_details,
    sync_fixture_visuals,
)
from soccera.logging import configure_logging, get_logger
from soccera.storage.database import session_scope
from soccera.storage.repositories import (
    LeagueRepository,
    MatchRepository,
    MatchVisualsRepository,
    SeasonRepository,
)

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("league_id")
    parser.add_argument("season_year", type=int)
    parser.add_argument("--finished-only", action="store_true", help="skip unplayed matches")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--only-missing", action="store_true", help="skip matches whose detail is up to date"
    )
    mode.add_argument(
        "--visuals-only",
        action="store_true",
        help="only shots/momentum/heatmaps, for finished matches without them",
    )
    parser.add_argument("--limit", type=int, default=None, help="max matches to process this run")
    parser.add_argument(
        "--pause", type=float, default=2.0, help="seconds to wait between matches (default 2)"
    )
    return parser.parse_args()


def pending_matches(adapter: SofascoreAdapter, args: argparse.Namespace) -> tuple[list[str], int]:
    """Source ids to process this run (oldest first) and how many qualified in total."""
    with session_scope() as session:
        league = LeagueRepository(session).get_by_source(adapter.source_name, args.league_id)
        if league is None:
            sys.exit(f"League {args.league_id} not synced — run run_backfill_sofascore.py first")
        season = SeasonRepository(session).get_by_league_and_year(league.id, args.season_year)
        if season is None:
            sys.exit(f"Season {args.season_year} not synced — run run_backfill_sofascore.py first")

        matches = MatchRepository(session).get_by_league_and_season(league.id, season.id)
        if args.finished_only:
            matches = [m for m in matches if m.status == "FINISHED"]
        if args.only_missing:
            matches = [m for m in matches if needs_details(m)]
        if args.visuals_only:
            matches = [m for m in matches if m.status == "FINISHED"]
            done = MatchVisualsRepository(session).match_ids_with_momentum([m.id for m in matches])
            matches = [m for m in matches if m.id not in done]
        matches.sort(key=lambda m: m.match_date)

        selected = matches[: args.limit] if args.limit else matches
        return [m.source_id for m in selected], len(matches)


def main() -> None:
    configure_logging()
    args = parse_args()

    adapter = SofascoreAdapter()
    synced, failed = 0, []
    try:
        source_ids, total = pending_matches(adapter, args)
        print(f"{total} matches qualify; processing {len(source_ids)} this run...")

        for i, source_id in enumerate(source_ids, 1):
            if i > 1:
                time.sleep(args.pause)
            try:
                with session_scope() as session:
                    if args.visuals_only:
                        match = MatchRepository(session).get_by_source(
                            adapter.source_name, source_id
                        )
                        sync_fixture_visuals(adapter, session, match)
                    else:
                        sync_fixture_details(adapter, session, source_id)
            except SofascoreError as exc:
                if exc.code == 403:
                    print(f"  [{i}/{len(source_ids)}] Blocked by Sofascore (403) — stopping. {exc}")
                    break
                failed.append(source_id)
                print(f"  [{i}/{len(source_ids)}] match {source_id} FAILED: {exc}")
                continue
            except Exception as exc:  # one bad payload shouldn't sink the whole batch
                logger.exception("sync.match_details_failed", match_source_id=source_id)
                failed.append(source_id)
                print(f"  [{i}/{len(source_ids)}] match {source_id} FAILED: {exc!r}")
                continue
            synced += 1
            print(f"  [{i}/{len(source_ids)}] match {source_id} done")
    finally:
        adapter.close()

    print(f"\nSynced {synced}, failed {len(failed)}.")
    if args.only_missing or args.visuals_only:
        _, still_missing = pending_matches(adapter, args)
        print(f"{still_missing} matches still pending — re-run to continue.")
    if failed:
        print("Failed match ids:", ", ".join(failed))


if __name__ == "__main__":
    main()
