"""
Per-team performance profile for a season, built from per-match team
statistics: expected goals for/against, shot volume and quality, and
expected points — what the table "should" look like given chance quality.
"""

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
from scipy.stats import poisson
from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.analytics.common import get_finished_matches
from soccera.storage.models.match_statistic import MatchStatistic

MAX_GOALS = 10


@dataclass
class TeamProfile:
    team_id: int
    team_name: str
    matches: int = 0  # matches with statistics
    points: int = 0
    expected_points: float = 0.0
    goals_for: int = 0
    goals_against: int = 0
    xg_for: float = 0.0
    xg_against: float = 0.0
    shots_for: float = 0.0
    shots_against: float = 0.0
    shots_on_target_for: float = 0.0
    shots_on_target_against: float = 0.0
    possession: float = 0.0  # average %
    per_match: dict[str, float] = field(default_factory=dict)


def expected_points(xg_own: float, xg_opponent: float) -> float:
    """Points a team would average if each side's goals were Poisson with
    its xG as the mean — the standard 'xPts' from a single match's chances."""
    goals = np.arange(MAX_GOALS + 1)
    grid = np.outer(poisson.pmf(goals, xg_own), poisson.pmf(goals, xg_opponent))
    grid /= grid.sum()
    win, draw = np.tril(grid, -1).sum(), np.trace(grid)
    return float(3 * win + draw)


def build_team_profiles(
    session: Session, source: str, league_source_id: str, season_year: int
) -> list[TeamProfile]:
    """Only matches that have statistics count (xG needs them), so `matches`
    can be lower than games played; per-match averages use that count."""
    matches = get_finished_matches(session, source, league_source_id, season_year)
    if not matches:
        return []

    stats: dict[tuple[int, int], dict[str, float]] = defaultdict(dict)
    rows = session.execute(
        select(MatchStatistic).where(MatchStatistic.match_id.in_([m.id for m in matches]))
    ).scalars()
    for row in rows:
        if row.stat_value is not None:
            stats[(row.match_id, row.team_id)][row.stat_type] = float(row.stat_value)

    profiles: dict[int, TeamProfile] = {}
    for m in matches:
        home, away = stats.get((m.id, m.home_team_id)), stats.get((m.id, m.away_team_id))
        if not home or not away or "expectedGoals" not in home or "expectedGoals" not in away:
            continue
        sides = (
            (m.home_team_id, m.home_team.name, home, away, m.home_score, m.away_score),
            (m.away_team_id, m.away_team.name, away, home, m.away_score, m.home_score),
        )
        for team_id, name, own, opp, scored, conceded in sides:
            p = profiles.setdefault(team_id, TeamProfile(team_id=team_id, team_name=name))
            p.matches += 1
            p.points += 3 if scored > conceded else 1 if scored == conceded else 0
            p.expected_points += expected_points(own["expectedGoals"], opp["expectedGoals"])
            p.goals_for += scored
            p.goals_against += conceded
            p.xg_for += own["expectedGoals"]
            p.xg_against += opp["expectedGoals"]
            p.shots_for += own.get("totalShotsOnGoal", 0)
            p.shots_against += opp.get("totalShotsOnGoal", 0)
            p.shots_on_target_for += own.get("shotsOnGoal", 0)
            p.shots_on_target_against += opp.get("shotsOnGoal", 0)
            p.possession += own.get("ballPossession", 0)

    result = []
    for p in profiles.values():
        n = p.matches
        p.possession = round(p.possession / n, 1)
        p.expected_points = round(p.expected_points, 1)
        p.xg_for, p.xg_against = round(p.xg_for, 2), round(p.xg_against, 2)
        p.per_match = {
            "xg_for": round(p.xg_for / n, 2),
            "xg_against": round(p.xg_against / n, 2),
            "shots_for": round(p.shots_for / n, 1),
            "shots_against": round(p.shots_against / n, 1),
            "shots_on_target_for": round(p.shots_on_target_for / n, 1),
            "xg_per_shot": round(p.xg_for / p.shots_for, 3) if p.shots_for else 0.0,
        }
        result.append(p)
    result.sort(key=lambda p: -(p.xg_for - p.xg_against))
    return result
