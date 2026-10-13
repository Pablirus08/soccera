"""
Translates API-Football's raw response shapes (schemas.py) into the
source-agnostic domain models (ingestion.domain). This is the only place
in the codebase that should know API-Football's field names and status
codes.
"""

from datetime import date

from soccera.ingestion.domain import (
    DomainLeague,
    DomainLeagueWithSeasons,
    DomainMatch,
    DomainMatchEvent,
    DomainMatchStatistic,
    DomainPlayer,
    DomainSeason,
    DomainTeam,
    DomainVenue,
)
from soccera.ingestion.providers.api_football.schemas import (
    RawFixtureEntry,
    RawFixtureEventEntry,
    RawFixtureStatisticsEntry,
    RawLeagueEntry,
    RawPlayerEntry,
    RawTeamEntry,
)

# API-Football's fixture.status.short codes -> our canonical match statuses.
STATUS_MAP: dict[str, str] = {
    "TBD": "SCHEDULED",
    "NS": "SCHEDULED",
    "1H": "LIVE",
    "2H": "LIVE",
    "ET": "LIVE",
    "BT": "LIVE",
    "P": "LIVE",
    "LIVE": "LIVE",
    "HT": "HALFTIME",
    "FT": "FINISHED",
    "AET": "FINISHED",
    "PEN": "FINISHED",
    "AWD": "FINISHED",
    "WO": "FINISHED",
    "PST": "POSTPONED",
    "CANC": "CANCELLED",
    "ABD": "CANCELLED",
    "SUSP": "SUSPENDED",
    "INT": "SUSPENDED",
}


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def map_league(raw: RawLeagueEntry) -> DomainLeagueWithSeasons:
    league = DomainLeague(
        source_id=str(raw.league.id),
        name=raw.league.name,
        country=raw.league.country,
        type=(raw.league.type or "League").lower(),
    )
    seasons = [
        DomainSeason(
            league_source_id=str(raw.league.id),
            year=s.year,
            start_date=_parse_date(s.start),
            end_date=_parse_date(s.end),
            is_current=s.current,
        )
        for s in raw.seasons
    ]
    return DomainLeagueWithSeasons(league=league, seasons=seasons)


def map_team(raw: RawTeamEntry) -> DomainTeam:
    venue = None
    if raw.venue and raw.venue.id is not None:
        venue = DomainVenue(
            source_id=str(raw.venue.id),
            name=raw.venue.name or "Unknown",
            city=raw.venue.city,
            capacity=raw.venue.capacity,
        )
    return DomainTeam(
        source_id=str(raw.team.id),
        name=raw.team.name,
        short_name=raw.team.code,
        country=raw.team.country,
        founded=raw.team.founded,
        venue=venue,
    )


def map_player(raw: RawPlayerEntry) -> DomainPlayer:
    games = raw.statistics[0].games if raw.statistics else None
    return DomainPlayer(
        source_id=str(raw.player.id),
        name=raw.player.name,
        first_name=raw.player.firstname,
        last_name=raw.player.lastname,
        birth_date=_parse_date(raw.player.birth.date if raw.player.birth else None),
        nationality=raw.player.nationality,
        position=games.position if games else None,
        shirt_number=games.number if games else None,
    )


def map_fixture(raw: RawFixtureEntry) -> DomainMatch:
    return DomainMatch(
        source_id=str(raw.fixture.id),
        league_source_id=str(raw.league.id),
        season_year=raw.league.season,
        home_team_source_id=str(raw.teams.home.id),
        away_team_source_id=str(raw.teams.away.id),
        venue_source_id=str(raw.fixture.venue.id) if raw.fixture.venue and raw.fixture.venue.id else None,
        match_date=raw.fixture.date,
        status=STATUS_MAP.get(raw.fixture.status.short, "SCHEDULED"),
        elapsed_minutes=raw.fixture.status.elapsed,
        round=raw.league.round,
        referee=raw.fixture.referee,
        home_score=raw.goals.home,
        away_score=raw.goals.away,
        home_score_ht=raw.score.halftime.home,
        away_score_ht=raw.score.halftime.away,
    )


def map_fixture_statistics(
    raw: RawFixtureStatisticsEntry, match_source_id: str
) -> list[DomainMatchStatistic]:
    results = []
    for stat in raw.statistics:
        value = stat.value
        numeric_value: float | None
        if isinstance(value, str):
            numeric_value = float(value.rstrip("%")) if value.rstrip("%").replace(".", "", 1).isdigit() else None
        else:
            numeric_value = value
        results.append(
            DomainMatchStatistic(
                match_source_id=match_source_id,
                team_source_id=str(raw.team.id),
                stat_type=stat.type.lower().replace(" ", "_"),
                stat_value=numeric_value,
            )
        )
    return results


def map_fixture_event(raw: RawFixtureEventEntry, match_source_id: str) -> DomainMatchEvent:
    return DomainMatchEvent(
        match_source_id=match_source_id,
        team_source_id=str(raw.team.id),
        player_source_id=str(raw.player.id) if raw.player and raw.player.id else None,
        related_player_source_id=str(raw.assist.id) if raw.assist and raw.assist.id else None,
        event_type=raw.type.upper(),
        event_detail=raw.detail,
        minute=raw.time.get("elapsed", 0),
        extra_minute=raw.time.get("extra"),
    )
