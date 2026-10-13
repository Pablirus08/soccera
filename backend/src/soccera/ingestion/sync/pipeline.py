"""
Reusable sync steps shared by historical backfills and live polling.
Each function only depends on DataSourceAdapter + ingestion.domain models
on the read side, and on repositories on the write side — no provider
specifics leak in here.
"""

from datetime import date

from sqlalchemy.orm import Session

from soccera.ingestion.base import DataSourceAdapter
from soccera.ingestion.domain import DomainMatch
from soccera.logging import get_logger
from soccera.storage.models.match_event import MatchEvent
from soccera.storage.repositories import (
    LeagueRepository,
    MatchEventRepository,
    MatchRepository,
    MatchStatisticRepository,
    PlayerRepository,
    SeasonRepository,
    TeamRepository,
    VenueRepository,
)

logger = get_logger(__name__)


def sync_leagues(
    adapter: DataSourceAdapter, session: Session, country: str | None = None
) -> int:
    league_repo = LeagueRepository(session)
    season_repo = SeasonRepository(session)
    count = 0
    for entry in adapter.get_leagues(country=country):
        league = league_repo.upsert(
            source=adapter.source_name,
            source_id=entry.league.source_id,
            name=entry.league.name,
            country=entry.league.country,
            type=entry.league.type,
        )
        for season in entry.seasons:
            # start_date/end_date aren't provided by every adapter (Sofascore
            # never sets them) — sync_fixtures derives them from actual match
            # dates instead, so we must not blank that out with None here.
            season_fields: dict[str, object] = {"is_current": season.is_current}
            if season.start_date is not None:
                season_fields["start_date"] = season.start_date
            if season.end_date is not None:
                season_fields["end_date"] = season.end_date
            season_repo.upsert(league_id=league.id, year=season.year, **season_fields)
        count += 1
    return count


def sync_teams(
    adapter: DataSourceAdapter, session: Session, league_source_id: str, season_year: int
) -> int:
    venue_repo = VenueRepository(session)
    team_repo = TeamRepository(session)
    count = 0
    for team in adapter.get_teams(league_source_id, season_year):
        venue_id = None
        if team.venue:
            venue = venue_repo.upsert(
                source=adapter.source_name,
                source_id=team.venue.source_id,
                name=team.venue.name,
                city=team.venue.city,
                country=team.venue.country,
                capacity=team.venue.capacity,
            )
            venue_id = venue.id
        team_repo.upsert(
            source=adapter.source_name,
            source_id=team.source_id,
            name=team.name,
            short_name=team.short_name,
            country=team.country,
            founded=team.founded,
            venue_id=venue_id,
        )
        count += 1
    return count


def sync_fixtures(
    adapter: DataSourceAdapter,
    session: Session,
    league_source_id: str,
    season_year: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> int:
    league_repo = LeagueRepository(session)
    season_repo = SeasonRepository(session)
    team_repo = TeamRepository(session)
    venue_repo = VenueRepository(session)
    match_repo = MatchRepository(session)

    league = league_repo.get_by_source(adapter.source_name, league_source_id)
    if league is None:
        raise ValueError(f"League {league_source_id} not synced yet — run sync_leagues first")
    season = season_repo.get_by_league_and_year(league.id, season_year)
    if season is None:
        raise ValueError(f"Season {season_year} for league {league_source_id} not synced yet")

    count = 0
    for fixture in adapter.get_fixtures(league_source_id, season_year, date_from, date_to):
        if _upsert_fixture(
            fixture, adapter.source_name, league.id, season.id, team_repo, venue_repo, match_repo
        ):
            count += 1

    if count:
        season_matches = match_repo.get_by_league_and_season(league.id, season.id)
        match_dates = [m.match_date.date() for m in season_matches]
        season_repo.upsert(
            league_id=league.id,
            year=season_year,
            start_date=min(match_dates),
            end_date=max(match_dates),
        )

    return count


def sync_live_fixtures(adapter: DataSourceAdapter, session: Session) -> int:
    """
    Upserts whatever the provider currently reports as live. Assumes the
    league/season/teams were already synced by a prior historical/backfill
    pass — fixtures for unknown leagues or teams are skipped and logged.
    """
    league_repo = LeagueRepository(session)
    season_repo = SeasonRepository(session)
    team_repo = TeamRepository(session)
    venue_repo = VenueRepository(session)
    match_repo = MatchRepository(session)

    count = 0
    for fixture in adapter.get_live_fixtures():
        league = league_repo.get_by_source(adapter.source_name, fixture.league_source_id)
        if league is None:
            logger.warning("sync.live_fixture_skipped_unknown_league", fixture_source_id=fixture.source_id)
            continue
        season = season_repo.get_by_league_and_year(league.id, fixture.season_year)
        if season is None:
            logger.warning("sync.live_fixture_skipped_unknown_season", fixture_source_id=fixture.source_id)
            continue
        if _upsert_fixture(
            fixture, adapter.source_name, league.id, season.id, team_repo, venue_repo, match_repo
        ):
            count += 1
    return count


def _upsert_fixture(
    fixture: DomainMatch,
    source: str,
    league_id: int,
    season_id: int,
    team_repo: TeamRepository,
    venue_repo: VenueRepository,
    match_repo: MatchRepository,
) -> bool:
    home_team = team_repo.get_by_source(source, fixture.home_team_source_id)
    away_team = team_repo.get_by_source(source, fixture.away_team_source_id)
    if home_team is None or away_team is None:
        logger.warning("sync.fixture_skipped_unknown_team", fixture_source_id=fixture.source_id)
        return False

    venue_id = None
    if fixture.venue_source_id:
        venue = venue_repo.get_by_source(source, fixture.venue_source_id)
        venue_id = venue.id if venue else None

    match_repo.upsert(
        source=source,
        source_id=fixture.source_id,
        league_id=league_id,
        season_id=season_id,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        venue_id=venue_id,
        match_date=fixture.match_date,
        status=fixture.status,
        elapsed_minutes=fixture.elapsed_minutes,
        round=fixture.round,
        referee=fixture.referee,
        home_score=fixture.home_score,
        away_score=fixture.away_score,
        home_score_ht=fixture.home_score_ht,
        away_score_ht=fixture.away_score_ht,
    )
    return True


def sync_fixture_details(adapter: DataSourceAdapter, session: Session, match_source_id: str) -> None:
    """Syncs events and statistics for a single match — called per live match each poll."""
    match_repo = MatchRepository(session)
    team_repo = TeamRepository(session)
    player_repo = PlayerRepository(session)
    event_repo = MatchEventRepository(session)
    stat_repo = MatchStatisticRepository(session)

    match = match_repo.get_by_source(adapter.source_name, match_source_id)
    if match is None:
        logger.warning("sync.fixture_details_skipped_unknown_match", match_source_id=match_source_id)
        return

    events: list[MatchEvent] = []
    for event in adapter.get_fixture_events(match_source_id):
        team = team_repo.get_by_source(adapter.source_name, event.team_source_id)
        if team is None:
            continue
        player = (
            player_repo.get_by_source(adapter.source_name, event.player_source_id)
            if event.player_source_id
            else None
        )
        related_player = (
            player_repo.get_by_source(adapter.source_name, event.related_player_source_id)
            if event.related_player_source_id
            else None
        )
        events.append(
            MatchEvent(
                match_id=match.id,
                team_id=team.id,
                player_id=player.id if player else None,
                related_player_id=related_player.id if related_player else None,
                event_type=event.event_type,
                event_detail=event.event_detail,
                minute=event.minute,
                extra_minute=event.extra_minute,
            )
        )
    event_repo.replace_for_match(match.id, events)

    for stat in adapter.get_fixture_statistics(match_source_id):
        team = team_repo.get_by_source(adapter.source_name, stat.team_source_id)
        if team is None:
            continue
        stat_repo.upsert(match.id, team.id, stat.stat_type, stat.stat_value)
