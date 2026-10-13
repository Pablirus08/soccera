from dataclasses import dataclass

from sqlalchemy.orm import Session

from soccera.analytics.common import get_finished_matches


@dataclass
class GoalStats:
    matches_played: int
    total_goals: int
    avg_goals_per_match: float
    btts_pct: float
    over_2_5_pct: float
    home_win_pct: float
    draw_pct: float
    away_win_pct: float


def build_goal_stats(
    session: Session, source: str, league_source_id: str, season_year: int
) -> GoalStats:
    matches = get_finished_matches(session, source, league_source_id, season_year)
    n = len(matches)
    if n == 0:
        return GoalStats(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    total_goals = sum(m.home_score + m.away_score for m in matches)
    btts = sum(1 for m in matches if m.home_score > 0 and m.away_score > 0)
    over_2_5 = sum(1 for m in matches if (m.home_score + m.away_score) > 2.5)
    home_wins = sum(1 for m in matches if m.home_score > m.away_score)
    draws = sum(1 for m in matches if m.home_score == m.away_score)
    away_wins = n - home_wins - draws

    return GoalStats(
        matches_played=n,
        total_goals=total_goals,
        avg_goals_per_match=total_goals / n,
        btts_pct=100 * btts / n,
        over_2_5_pct=100 * over_2_5 / n,
        home_win_pct=100 * home_wins / n,
        draw_pct=100 * draws / n,
        away_win_pct=100 * away_wins / n,
    )
