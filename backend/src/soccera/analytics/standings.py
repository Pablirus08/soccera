from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from soccera.analytics.common import get_finished_matches


@dataclass
class TeamStanding:
    team_id: int
    team_name: str
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0

    @property
    def goal_diff(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points(self) -> int:
        return self.won * 3 + self.drawn


@dataclass
class Standings:
    league_source_id: str
    season_year: int
    rows: list[TeamStanding] = field(default_factory=list)


def build_standings(
    session: Session, source: str, league_source_id: str, season_year: int
) -> Standings:
    matches = get_finished_matches(session, source, league_source_id, season_year)

    table: dict[int, TeamStanding] = {}

    def row_for(team_id: int, team_name: str) -> TeamStanding:
        if team_id not in table:
            table[team_id] = TeamStanding(team_id=team_id, team_name=team_name)
        return table[team_id]

    for m in matches:
        home = row_for(m.home_team_id, m.home_team.name)
        away = row_for(m.away_team_id, m.away_team.name)

        home.played += 1
        away.played += 1
        home.goals_for += m.home_score
        home.goals_against += m.away_score
        away.goals_for += m.away_score
        away.goals_against += m.home_score

        if m.home_score > m.away_score:
            home.won += 1
            away.lost += 1
        elif m.home_score < m.away_score:
            away.won += 1
            home.lost += 1
        else:
            home.drawn += 1
            away.drawn += 1

    rows = sorted(table.values(), key=lambda t: (-t.points, -t.goal_diff, -t.goals_for))
    return Standings(league_source_id=league_source_id, season_year=season_year, rows=rows)
