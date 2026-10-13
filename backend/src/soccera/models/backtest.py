"""
Walk-forward evaluation: each test tournament is predicted by a model fit
only on matches played before that tournament started, so no information
from the future leaks into a prediction. Scores are compared against a
baseline that always predicts the training set's home/draw/away frequencies.
"""

import math
from dataclasses import dataclass
from datetime import datetime

from soccera.models.poisson import MatchResult, PoissonModel, time_decay_weights

HOME, DRAW, AWAY = 0, 1, 2


@dataclass(frozen=True)
class HistoricalMatch:
    match_date: datetime
    tournament: str
    result: MatchResult


@dataclass
class Scores:
    n: int = 0
    log_loss: float = 0.0
    brier: float = 0.0
    correct: int = 0

    def add(self, probs: tuple[float, float, float], outcome: int) -> None:
        self.n += 1
        self.log_loss += -math.log(max(probs[outcome], 1e-12))
        self.brier += sum((p - (1.0 if k == outcome else 0.0)) ** 2 for k, p in enumerate(probs))
        self.correct += int(max(range(3), key=lambda k: probs[k]) == outcome)

    def merge(self, other: "Scores") -> None:
        self.n += other.n
        self.log_loss += other.log_loss
        self.brier += other.brier
        self.correct += other.correct

    @property
    def mean_log_loss(self) -> float:
        return self.log_loss / self.n

    @property
    def mean_brier(self) -> float:
        return self.brier / self.n

    @property
    def accuracy(self) -> float:
        return self.correct / self.n


@dataclass
class TournamentReport:
    tournament: str
    train_size: int
    model: Scores
    baseline: Scores


def outcome_of(r: MatchResult) -> int:
    if r.home_goals > r.away_goals:
        return HOME
    if r.home_goals == r.away_goals:
        return DRAW
    return AWAY


def outcome_frequencies(results: list[MatchResult]) -> tuple[float, float, float]:
    counts = [0, 0, 0]
    for r in results:
        counts[outcome_of(r)] += 1
    n = len(results)
    return counts[0] / n, counts[1] / n, counts[2] / n


def walk_forward(
    matches: list[HistoricalMatch],
    test_tournaments: list[str],
    half_life_days: float | None = None,
) -> list[TournamentReport]:
    """`half_life_days` enables time decay, measured from each test tournament's start."""
    matches = sorted(matches, key=lambda m: m.match_date)
    reports = []
    for tournament in test_tournaments:
        test = [m for m in matches if m.tournament == tournament]
        if not test:
            continue
        start = test[0].match_date
        train_matches = [m for m in matches if m.match_date < start]
        train = [m.result for m in train_matches]
        weights = (
            time_decay_weights([m.match_date for m in train_matches], start, half_life_days)
            if half_life_days
            else None
        )

        model = PoissonModel.fit(train, weights)
        baseline_probs = outcome_frequencies(train)

        model_scores, baseline_scores = Scores(), Scores()
        for m in test:
            p = model.predict(m.result.home_team_id, m.result.away_team_id)
            outcome = outcome_of(m.result)
            model_scores.add((p.home_win, p.draw, p.away_win), outcome)
            baseline_scores.add(baseline_probs, outcome)

        reports.append(TournamentReport(tournament, len(train), model_scores, baseline_scores))
    return reports
