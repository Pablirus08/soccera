"""
Translates Sofascore's raw response shapes (schemas.py) into the
source-agnostic domain models (ingestion.domain). This is the only place
in the codebase that should know Sofascore's field names and status codes.
"""

from datetime import datetime, timezone

from soccera.ingestion.domain import (
    DomainMatch,
    DomainMatchEvent,
    DomainMatchStatistic,
    DomainPlayer,
    DomainTeam,
)
from soccera.ingestion.providers.costa_rica.schemas import (
    RawEventEntry,
    RawIncidentEntry,
    RawSquadPlayer,
    RawStatisticPeriod,
    RawTeamRef,
)

# Sofascore's event.status.type -> our canonical match statuses.
STATUS_MAP: dict[str, str] = {
    "notstarted": "SCHEDULED",
    "inprogress": "LIVE",
    "finished": "FINISHED",
    "postponed": "POSTPONED",
    "canceled": "CANCELLED",
    "cancelled": "CANCELLED",
    "abandoned": "CANCELLED",
    "interrupted": "SUSPENDED",
    "suspended": "SUSPENDED",
}

EVENT_TYPE_MAP: dict[str, str] = {
    "goal": "GOAL",
    "card": "CARD",
    "substitution": "SUBST",
}


def season_year_from_sofascore_year(year_str: str) -> int:
    """Sofascore names recent seasons like "26/27" (Apertura) or "25/26"
    (Clausura) — we key our season_year on the first half: "26/27" -> 2026.
    Seasons from 2008-2011 are a plain 4-digit year with no slash ("2011")
    and are used as-is."""
    if "/" in year_str:
        return 2000 + int(year_str.split("/")[0])
    return int(year_str)


def map_team(raw: RawTeamRef, country: str = "Costa Rica") -> DomainTeam:
    return DomainTeam(
        source_id=str(raw.id),
        name=raw.name,
        short_name=raw.nameCode,
        country=country,
    )


def map_fixture(raw: RawEventEntry, league_source_id: str, season_year: int) -> DomainMatch:
    status = STATUS_MAP.get(raw.status.type, "SCHEDULED")
    if status == "LIVE" and raw.status.description and "half" in raw.status.description.lower():
        status = "HALFTIME"

    round_value = None
    if raw.roundInfo:
        round_value = raw.roundInfo.name or (
            str(raw.roundInfo.round) if raw.roundInfo.round is not None else None
        )

    return DomainMatch(
        source_id=str(raw.id),
        league_source_id=league_source_id,
        season_year=season_year,
        home_team_source_id=str(raw.homeTeam.id),
        away_team_source_id=str(raw.awayTeam.id),
        venue_source_id=None,
        match_date=datetime.fromtimestamp(raw.startTimestamp, tz=timezone.utc),
        status=status,
        round=round_value,
        home_score=raw.homeScore.current,
        away_score=raw.awayScore.current,
        home_score_ht=raw.homeScore.period1,
        away_score_ht=raw.awayScore.period1,
    )


def map_fixture_event(
    raw: RawIncidentEntry, match_source_id: str, home_team_id: str, away_team_id: str
) -> DomainMatchEvent | None:
    """Returns None for incident types we don't track (period markers, VAR
    decisions, etc.) or when the side can't be determined."""
    event_type = EVENT_TYPE_MAP.get(raw.incidentType)
    if event_type is None or raw.isHome is None:
        return None

    team_source_id = home_team_id if raw.isHome else away_team_id

    if raw.incidentType == "substitution":
        player_id = str(raw.playerIn.id) if raw.playerIn else None
        related_id = str(raw.playerOut.id) if raw.playerOut else None
    else:
        player_id = str(raw.player.id) if raw.player else None
        related_id = str(raw.assist1.id) if raw.assist1 else None

    # addedTime uses a 999 sentinel for "not applicable" on non-time incidents.
    extra_minute = raw.addedTime if raw.addedTime and raw.addedTime < 900 else None

    return DomainMatchEvent(
        match_source_id=match_source_id,
        team_source_id=team_source_id,
        player_source_id=player_id,
        related_player_source_id=related_id,
        event_type=event_type,
        event_detail=raw.incidentClass,
        minute=raw.time or 0,
        extra_minute=extra_minute,
    )


def map_fixture_statistics(
    periods: list[RawStatisticPeriod], match_source_id: str, home_team_id: str, away_team_id: str
) -> list[DomainMatchStatistic]:
    all_period = next((p for p in periods if p.period == "ALL"), periods[0] if periods else None)
    if all_period is None:
        return []

    results: list[DomainMatchStatistic] = []
    for group in all_period.groups:
        for item in group.statisticsItems:
            if item.homeValue is not None:
                results.append(
                    DomainMatchStatistic(
                        match_source_id=match_source_id,
                        team_source_id=home_team_id,
                        stat_type=item.key,
                        stat_value=item.homeValue,
                    )
                )
            if item.awayValue is not None:
                results.append(
                    DomainMatchStatistic(
                        match_source_id=match_source_id,
                        team_source_id=away_team_id,
                        stat_type=item.key,
                        stat_value=item.awayValue,
                    )
                )
    return results


def map_player(raw: RawSquadPlayer) -> DomainPlayer:
    birth_date = None
    if raw.dateOfBirthTimestamp:
        birth_date = datetime.fromtimestamp(raw.dateOfBirthTimestamp, tz=timezone.utc).date()
    shirt_number = int(raw.jerseyNumber) if raw.jerseyNumber and raw.jerseyNumber.isdigit() else None
    return DomainPlayer(
        source_id=str(raw.id),
        name=raw.name,
        first_name=raw.firstName,
        last_name=raw.lastName,
        birth_date=birth_date,
        position=raw.position,
        shirt_number=shirt_number,
    )
