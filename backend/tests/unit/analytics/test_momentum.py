from soccera.analytics.momentum import (
    Spell,
    find_spells,
    oriented,
    summarize_side,
    timeline_minute,
)
from soccera.ingestion.sync.pipeline import bin_heatmap
from soccera.storage.models.match_visuals import HEATMAP_COLS, HEATMAP_ROWS


def _curve(values: list[float]) -> list[tuple[float, float]]:
    return [(float(i), v) for i, v in enumerate(values)]


def test_stoppage_time_collapses_onto_the_curve():
    assert timeline_minute(30, None) == 30
    assert timeline_minute(45, 3) == 45.5
    assert timeline_minute(90, 4) == 90.5


def test_sustained_pressure_is_a_spell_but_a_blip_is_not():
    values = [0] * 10 + [50] * 8 + [0] * 10 + [80] + [0] * 10
    spells = find_spells(_curve(values))
    assert len(spells) == 1
    assert 9 <= spells[0].start <= 11 and spells[0].minutes >= 4


def test_orientation_flips_the_away_side():
    assert oriented([[10, 30]], home=False) == [(10, -30)]


def test_goal_right_after_a_spell_counts_as_converted():
    curve = _curve([0] * 10 + [50] * 8 + [0] * 20)
    summary = summarize_side(curve, goal_minutes=[18.5], shots=[(15.0, 0.3)])
    assert summary.spells_converted == 1
    assert summary.goals_in_spells == 1
    assert summary.xg_in_spells == 0.3


def test_spell_contains_respects_grace():
    s = Spell(10, 20)
    assert s.contains(21.5, grace=2) and not s.contains(21.5)


def test_heatmap_binning_counts_every_point_in_range():
    grid = bin_heatmap([(0, 0), (100, 100), (50, 50), (99.9, 0.1)])
    assert len(grid) == HEATMAP_ROWS * HEATMAP_COLS
    assert sum(grid) == 4
    assert grid[0] == 1  # (0, 0) -> top-left cell
    assert grid[-1] == 1  # (100, 100) clamps into the last cell
