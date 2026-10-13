import pytest

from soccera.analytics.players import match_weight, shrink_rating


def test_match_weight_is_share_of_ninety_minutes_capped():
    assert match_weight(90) == 1
    assert match_weight(45) == 0.5
    assert match_weight(120) == 1  # extra time doesn't overweight
    assert match_weight(None) == 0


def test_one_great_cameo_stays_close_to_the_position_mean():
    # A single 8.0 in 25 minutes vs. a 6.7 position average.
    adjusted = shrink_rating(8.0 * match_weight(25), match_weight(25), prior=6.7)
    assert adjusted == pytest.approx(6.77, abs=0.01)


def test_a_consistent_season_outranks_a_single_high_rating():
    one_game = shrink_rating(8.0, 1.0, prior=6.7)
    ten_games = shrink_rating(7.5 * 10, 10.0, prior=6.7)
    assert ten_games > one_game
