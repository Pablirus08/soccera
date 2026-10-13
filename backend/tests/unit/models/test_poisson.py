from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from soccera.models.poisson import MatchResult, PoissonModel, time_decay_weights


def _simulate(strength: dict[int, tuple[float, float]], home_adv: float, rounds: int, seed: int = 0):
    rng = np.random.default_rng(seed)
    results = []
    teams = list(strength)
    for _ in range(rounds):
        for h in teams:
            for a in teams:
                if h == a:
                    continue
                lam_h = np.exp(home_adv + strength[h][0] - strength[a][1])
                lam_a = np.exp(strength[a][0] - strength[h][1])
                results.append(MatchResult(h, a, int(rng.poisson(lam_h)), int(rng.poisson(lam_a))))
    return results


def test_recovers_known_parameters():
    truth = {1: (0.4, 0.3), 2: (0.0, 0.0), 3: (-0.4, -0.3)}
    model = PoissonModel.fit(_simulate(truth, home_adv=0.3, rounds=150))

    assert model.home_advantage == pytest.approx(0.3, abs=0.05)
    assert model.attack[1] > model.attack[2] > model.attack[3]
    assert model.defense[1] > model.defense[2] > model.defense[3]


def test_probabilities_are_a_distribution_and_favor_stronger_team():
    truth = {1: (0.5, 0.4), 2: (-0.5, -0.4)}
    model = PoissonModel.fit(_simulate(truth, home_adv=0.25, rounds=100))

    strong_home = model.predict(1, 2)
    weak_home = model.predict(2, 1)

    for p in (strong_home, weak_home):
        assert p.home_win + p.draw + p.away_win == pytest.approx(1.0)
    assert strong_home.home_win > 0.6
    assert weak_home.away_win > weak_home.home_win


def test_unseen_team_is_treated_as_average():
    model = PoissonModel.fit(_simulate({1: (0.0, 0.0), 2: (0.0, 0.0)}, 0.2, rounds=50))
    lam_h, lam_a = model.expected_goals(999, 998)
    assert lam_h == pytest.approx(np.exp(model.home_advantage))
    assert lam_a == pytest.approx(1.0)


def test_time_decay_halves_weight_every_half_life():
    ref = datetime(2026, 10, 1, tzinfo=UTC)
    dates = [ref, ref - timedelta(days=180), ref - timedelta(days=360)]
    assert time_decay_weights(dates, ref, 180) == pytest.approx([1.0, 0.5, 0.25])
