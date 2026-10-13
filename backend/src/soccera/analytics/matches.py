from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from soccera.analytics.common import get_league_and_season
from soccera.storage.repositories import MatchRepository


@dataclass
class MatchListItem:
    source_id: str
    round: str | None
    match_date: datetime
    status: str
    home_team: str
    away_team: str
    home_score: int | None
    away_score: int | None


def build_match_list(
    session: Session, source: str, league_source_id: str, season_year: int
) -> list[MatchListItem]:
    league, season = get_league_and_season(session, source, league_source_id, season_year)
    matches = MatchRepository(session).get_by_league_and_season(league.id, season.id)
    matches.sort(key=lambda m: m.match_date)
    return [
        MatchListItem(
            source_id=m.source_id,
            round=m.round,
            match_date=m.match_date,
            status=m.status,
            home_team=m.home_team.name,
            away_team=m.away_team.name,
            home_score=m.home_score,
            away_score=m.away_score,
        )
        for m in matches
    ]
