"""
Independent-Poisson goals model (Maher, 1982):

    log(home goals expected) = home_advantage + attack[home] - defense[away]
    log(away goals expected) =                  attack[away] - defense[home]

Higher attack = scores more; higher defense = concedes less. Fit by maximum
likelihood with a small L2 penalty, which also pins down the otherwise free
offset between attack and defense and keeps teams with few matches near
average. Dixon-Coles' low-score correction and time decay are not here yet.
"""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.stats import poisson

MODEL_NAME = "poisson"
MODEL_VERSION = "1"
MAX_GOALS = 10
L2_PENALTY = 0.01


@dataclass(frozen=True)
class MatchResult:
    home_team_id: int
    away_team_id: int
    home_goals: int
    away_goals: int


@dataclass(frozen=True)
class OutcomeProbabilities:
    expected_home_goals: float
    expected_away_goals: float
    home_win: float
    draw: float
    away_win: float


class PoissonModel:
    def __init__(self, home_advantage: float, attack: dict[int, float], defense: dict[int, float]):
        self.home_advantage = home_advantage
        self.attack = attack
        self.defense = defense

    @classmethod
    def fit(cls, results: list[MatchResult]) -> "PoissonModel":
        team_ids = sorted({r.home_team_id for r in results} | {r.away_team_id for r in results})
        if len(team_ids) < 2:
            raise ValueError("Need matches between at least 2 teams to fit")
        index = {tid: i for i, tid in enumerate(team_ids)}
        n = len(team_ids)

        home = np.array([index[r.home_team_id] for r in results])
        away = np.array([index[r.away_team_id] for r in results])
        home_goals = np.array([r.home_goals for r in results], dtype=float)
        away_goals = np.array([r.away_goals for r in results], dtype=float)

        def neg_log_likelihood(params: np.ndarray) -> tuple[float, np.ndarray]:
            home_adv, attack, defense = params[0], params[1 : n + 1], params[n + 1 :]
            log_lam_h = home_adv + attack[home] - defense[away]
            log_lam_a = attack[away] - defense[home]
            lam_h, lam_a = np.exp(log_lam_h), np.exp(log_lam_a)

            # Poisson log-likelihood without the constant log(k!) term.
            ll = np.sum(home_goals * log_lam_h - lam_h + away_goals * log_lam_a - lam_a)
            penalty = L2_PENALTY * (np.sum(attack**2) + np.sum(defense**2))

            resid_h, resid_a = home_goals - lam_h, away_goals - lam_a
            grad = np.zeros_like(params)
            grad[0] = -np.sum(resid_h)
            g_attack = -(np.bincount(home, resid_h, n) + np.bincount(away, resid_a, n))
            g_defense = np.bincount(away, resid_h, n) + np.bincount(home, resid_a, n)
            grad[1 : n + 1] = g_attack + 2 * L2_PENALTY * attack
            grad[n + 1 :] = g_defense + 2 * L2_PENALTY * defense
            return -ll + penalty, grad

        result = minimize(neg_log_likelihood, np.zeros(2 * n + 1), jac=True, method="L-BFGS-B")
        if not result.success:
            raise RuntimeError(f"Poisson fit did not converge: {result.message}")

        params = result.x
        return cls(
            home_advantage=float(params[0]),
            attack={tid: float(params[1 + i]) for tid, i in index.items()},
            defense={tid: float(params[n + 1 + i]) for tid, i in index.items()},
        )

    def expected_goals(self, home_team_id: int, away_team_id: int) -> tuple[float, float]:
        # Teams unseen in training (e.g. newly promoted) are treated as average.
        att_h, def_h = self.attack.get(home_team_id, 0.0), self.defense.get(home_team_id, 0.0)
        att_a, def_a = self.attack.get(away_team_id, 0.0), self.defense.get(away_team_id, 0.0)
        lam_h = float(np.exp(self.home_advantage + att_h - def_a))
        lam_a = float(np.exp(att_a - def_h))
        return lam_h, lam_a

    def predict(self, home_team_id: int, away_team_id: int) -> OutcomeProbabilities:
        lam_h, lam_a = self.expected_goals(home_team_id, away_team_id)
        goals = np.arange(MAX_GOALS + 1)
        # grid[i, j] = P(home scores i, away scores j)
        grid = np.outer(poisson.pmf(goals, lam_h), poisson.pmf(goals, lam_a))
        home_win, draw, away_win = np.tril(grid, -1).sum(), np.trace(grid), np.triu(grid, 1).sum()
        total = home_win + draw + away_win  # renormalize the truncated tail
        return OutcomeProbabilities(
            expected_home_goals=lam_h,
            expected_away_goals=lam_a,
            home_win=float(home_win / total),
            draw=float(draw / total),
            away_win=float(away_win / total),
        )
