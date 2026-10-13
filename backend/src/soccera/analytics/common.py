"""
Shared lookups used by every analytics module. Analytics functions take a
plain SQLAlchemy Session (caller owns the session_scope) and return plain
dataclasses — no printing, no CLI concerns. That keeps this layer reusable
from the CLI today and from a future web API without changes.
"""

from sqlalchemy.orm import Session

from soccera.storage.models.league import League
from soccera.storage.models.match import Match
from soccera.storage.models.season import Season
from soccera.storage.repositories import LeagueRepository, MatchRepository, SeasonRepository


def get_league_and_season(
    session: Session, source: str, league_source_id: str, season_year: int
) -> tuple[League, Season]:
    league = LeagueRepository(session).get_by_source(source, league_source_id)
    if league is None:
        raise ValueError(f"League {league_source_id!r} not found for source {source!r}")

    season = SeasonRepository(session).get_by_league_and_year(league.id, season_year)
    if season is None:
        raise ValueError(f"Season {season_year} not found for league {league_source_id!r}")

    return league, season


def get_finished_matches(
    session: Session, source: str, league_source_id: str, season_year: int
) -> list[Match]:
    league, season = get_league_and_season(session, source, league_source_id, season_year)
    matches = MatchRepository(session).get_by_league_and_season(league.id, season.id)
    return [m for m in matches if m.status == "FINISHED"]
