"""
Next-round predictions and team strength ratings from the Poisson model,
fit on every finished match of the source (all tournaments, both
Apertura and Clausura). The walk-forward backtest (scripts/run_backtest.py)
found no gain from time decay on this league's data, so all matches weigh
the same.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from math import exp

import numpy as np
from sqlalchemy.orm import Session

from soccera.analytics.common import get_league_and_season
from soccera.models.poisson import MatchResult, PoissonModel
from soccera.storage.repositories import MatchRepository


@dataclass
class MatchPrediction:
    source_id: str
    round: str | None
    match_date: datetime
    home_team: str
    away_team: str
    expected_home_goals: float
    expected_away_goals: float
    home_win: float
    draw: float
    away_win: float
    likely_score: str  # most probable exact score, e.g. "1-0"
    likely_score_prob: float
    over_2_5: float
    both_score: float


@dataclass
class TeamRating:
    team_id: int
    team_name: str
    attack: float  # goals scored vs. an average team (1.20 = 20% more)
    defense: float  # goals conceded factor inverted (1.20 = concedes ~17% less)
    strength: float  # attack * defense: overall multiplier used to rank


@dataclass
class Predictions:
    trained_on: int
    home_advantage: float  # multiplier on the home side's expected goals
    matches: list[MatchPrediction]
    ratings: list[TeamRating]


def build_predictions(
    session: Session, source: str, league_source_id: str, season_year: int
) -> Predictions:
    league, season = get_league_and_season(session, source, league_source_id, season_year)
    match_repo = MatchRepository(session)

    history = match_repo.get_finished(source)
    model = PoissonModel.fit(
        [MatchResult(m.home_team_id, m.away_team_id, m.home_score, m.away_score) for m in history]
    )

    now = datetime.now(UTC)
    season_matches = match_repo.get_by_league_and_season(league.id, season.id)
    upcoming = sorted(
        (m for m in season_matches if m.status == "SCHEDULED" and m.match_date > now),
        key=lambda m: m.match_date,
    )
    next_round = upcoming[0].round if upcoming else None
    fixtures = [m for m in upcoming if m.round == next_round]

    predictions = []
    for m in fixtures:
        p = model.predict(m.home_team_id, m.away_team_id)
        grid = model.score_matrix(m.home_team_id, m.away_team_id)
        grid = grid / grid.sum()
        i, j = np.unravel_index(np.argmax(grid), grid.shape)
        goals = np.add.outer(np.arange(grid.shape[0]), np.arange(grid.shape[1]))
        predictions.append(
            MatchPrediction(
                source_id=m.source_id,
                round=m.round,
                match_date=m.match_date,
                home_team=m.home_team.name,
                away_team=m.away_team.name,
                expected_home_goals=round(p.expected_home_goals, 2),
                expected_away_goals=round(p.expected_away_goals, 2),
                home_win=round(p.home_win, 3),
                draw=round(p.draw, 3),
                away_win=round(p.away_win, 3),
                likely_score=f"{i}-{j}",
                likely_score_prob=round(float(grid[i, j]), 3),
                over_2_5=round(float(grid[goals > 2.5].sum()), 3),
                both_score=round(float(grid[1:, 1:].sum()), 3),
            )
        )

    # Rate only the teams actually playing this season (a withdrawn team
    # still appears in its cancelled fixtures).
    active = [m for m in season_matches if m.status != "CANCELLED"]
    season_teams = {m.home_team_id: m.home_team.name for m in active}
    season_teams.update({m.away_team_id: m.away_team.name for m in active})
    ratings = []
    for team_id, name in season_teams.items():
        if team_id not in model.attack:
            continue
        attack, defense = exp(model.attack[team_id]), exp(model.defense[team_id])
        strength = round(attack * defense, 2)
        ratings.append(TeamRating(team_id, name, round(attack, 2), round(defense, 2), strength))
    ratings.sort(key=lambda r: -r.strength)

    return Predictions(
        trained_on=len(history),
        home_advantage=round(exp(model.home_advantage), 2),
        matches=predictions,
        ratings=ratings,
    )
