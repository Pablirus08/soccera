"""
Averages built from match_statistics (possession, shots, corners, etc.).
Only populated for sources that actually report per-match stats — right
now that's Sofascore; API-Football's free-plan Costa Rica data has none,
so this simply returns an empty list for that source.
"""

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.analytics.common import get_finished_matches
from soccera.storage.models.match_statistic import MatchStatistic


@dataclass
class TeamStatAverages:
    team_id: int
    team_name: str
    averages: dict[str, float] = field(default_factory=dict)


def build_match_stat_averages(
    session: Session, source: str, league_source_id: str, season_year: int
) -> list[TeamStatAverages]:
    matches = get_finished_matches(session, source, league_source_id, season_year)
    match_ids = [m.id for m in matches]
    if not match_ids:
        return []

    teams_by_id = {}
    for m in matches:
        teams_by_id[m.home_team_id] = m.home_team.name
        teams_by_id[m.away_team_id] = m.away_team.name

    stmt = select(MatchStatistic).where(MatchStatistic.match_id.in_(match_ids))
    stats = session.execute(stmt).scalars()

    raw: dict[int, dict[str, list[float]]] = {}
    for stat in stats:
        if stat.stat_value is None:
            continue
        raw.setdefault(stat.team_id, {}).setdefault(stat.stat_type, []).append(float(stat.stat_value))

    result = [
        TeamStatAverages(
            team_id=team_id,
            team_name=teams_by_id.get(team_id, "?"),
            averages={stat_type: sum(values) / len(values) for stat_type, values in stat_map.items()},
        )
        for team_id, stat_map in raw.items()
    ]
    return sorted(result, key=lambda t: t.team_name)
