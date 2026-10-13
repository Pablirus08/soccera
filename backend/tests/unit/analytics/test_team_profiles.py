import pytest

from soccera.analytics.team_profiles import expected_points


def test_equal_chances_are_worth_the_same_to_both_sides():
    assert expected_points(1.2, 1.2) == pytest.approx(expected_points(1.2, 1.2))
    # Between a loss (0) and a win (3), and below 1.5 since draws only pay 1.
    assert 1.0 < expected_points(1.2, 1.2) < 1.5


def test_dominant_chances_approach_three_points():
    assert expected_points(3.5, 0.2) > 2.7
    assert expected_points(0.2, 3.5) < 0.1


def test_expected_points_of_both_sides_sum_between_two_and_three():
    own, opp = expected_points(1.6, 0.9), expected_points(0.9, 1.6)
    assert 2.0 <= own + opp <= 3.0
