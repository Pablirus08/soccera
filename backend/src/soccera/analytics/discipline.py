from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.analytics.common import get_finished_matches
from soccera.storage.models.match_event import MatchEvent


@dataclass
class TeamDiscipline:
    team_id: int
    team_name: str
    yellow_cards: int = 0
    red_cards: int = 0

    @property
    def total_cards(self) -> int:
        return self.yellow_cards + self.red_cards


def build_discipline(
    session: Session, source: str, league_source_id: str, season_year: int
) -> list[TeamDiscipline]:
    matches = get_finished_matches(session, source, league_source_id, season_year)
    match_ids = [m.id for m in matches]
    if not match_ids:
        return []

    teams_by_id = {}
    for m in matches:
        teams_by_id[m.home_team_id] = m.home_team.name
        teams_by_id[m.away_team_id] = m.away_team.name

    stmt = select(MatchEvent).where(
        MatchEvent.match_id.in_(match_ids), MatchEvent.event_type == "CARD"
    )
    events = session.execute(stmt).scalars()

    table: dict[int, TeamDiscipline] = {}
    for event in events:
        entry = table.setdefault(
            event.team_id,
            TeamDiscipline(team_id=event.team_id, team_name=teams_by_id.get(event.team_id, "?")),
        )
        if "red" in (event.event_detail or "").lower():
            entry.red_cards += 1
        else:
            entry.yellow_cards += 1

    return sorted(table.values(), key=lambda t: -t.total_cards)
