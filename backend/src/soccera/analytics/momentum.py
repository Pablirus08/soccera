"""
Momentum analysis on Sofascore's attacking-pressure curve (one point every
~0.5-1 minute; > 0 = home pressing, < 0 = away; stoppage time is squeezed
into minute 45.5 and 90.5).

A *spell* is a stretch where one team clearly dominates: the curve,
smoothed with a centered moving average, stays at or above SPELL_THRESHOLD
in that team's favour for at least SPELL_MIN_MINUTES. A spell is *converted*
when the team scores during it or within CONVERSION_GRACE_MINUTES after it
ends (pressure often turns into a goal right after the curve dips).
"""

from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.analytics.common import get_finished_matches
from soccera.storage.models.match import Match
from soccera.storage.models.match_event import MatchEvent
from soccera.storage.models.match_visuals import MatchMomentum, MatchShot

SMOOTHING_WINDOW = 5  # points (~3-5 minutes)
SPELL_THRESHOLD = 20  # roughly the 60th percentile of |pressure| in this league
SPELL_MIN_MINUTES = 4.0
CONVERSION_GRACE_MINUTES = 2.0


@dataclass(frozen=True)
class Spell:
    start: float
    end: float

    @property
    def minutes(self) -> float:
        return self.end - self.start

    def contains(self, minute: float, grace: float = 0.0) -> bool:
        return self.start <= minute <= self.end + grace


def timeline_minute(minute: int, extra_minute: int | None) -> float:
    """Event clock -> curve minute: stoppage time collapses to 45.5 / 90.5."""
    if extra_minute:
        return 45.5 if minute <= 45 else 90.5
    return float(minute)


def smooth(values: list[float], window: int = SMOOTHING_WINDOW) -> list[float]:
    half = window // 2
    out = []
    for i in range(len(values)):
        chunk = values[max(0, i - half) : i + half + 1]
        out.append(sum(chunk) / len(chunk))
    return out


def find_spells(
    points: list[tuple[float, float]],
    threshold: float = SPELL_THRESHOLD,
    min_minutes: float = SPELL_MIN_MINUTES,
) -> list[Spell]:
    """Spells where the (already team-oriented) curve stays >= threshold."""
    if not points:
        return []
    minutes = [p[0] for p in points]
    values = smooth([p[1] for p in points])
    spells, start = [], None
    for minute, value in zip(minutes, values, strict=True):
        if value >= threshold and start is None:
            start = minute
        elif value < threshold and start is not None:
            spells.append(Spell(start, minute))
            start = None
    if start is not None:
        spells.append(Spell(start, minutes[-1]))
    return [s for s in spells if s.minutes >= min_minutes]


def oriented(points: list[list[float]], home: bool) -> list[tuple[float, float]]:
    """Curve from one team's point of view: > 0 means *that* team presses."""
    sign = 1 if home else -1
    return [(p[0], sign * p[1]) for p in points]


@dataclass
class MatchMomentumSummary:
    spells: list[Spell]
    spells_converted: int
    goals: int
    goals_in_spells: int
    xg_in_spells: float
    share: float  # fraction of curve points in this team's favour


def summarize_side(
    curve: list[tuple[float, float]],
    goal_minutes: list[float],
    shots: list[tuple[float, float]],  # (minute, xg) for this team
) -> MatchMomentumSummary:
    spells = find_spells(curve)
    in_spell = lambda m: any(s.contains(m, CONVERSION_GRACE_MINUTES) for s in spells)  # noqa: E731
    return MatchMomentumSummary(
        spells=spells,
        spells_converted=sum(
            any(s.contains(g, CONVERSION_GRACE_MINUTES) for g in goal_minutes) for s in spells
        ),
        goals=len(goal_minutes),
        goals_in_spells=sum(in_spell(g) for g in goal_minutes),
        xg_in_spells=sum(xg for m, xg in shots if any(s.contains(m) for s in spells)),
        share=sum(v > 0 for _, v in curve) / len(curve) if curve else 0.0,
    )


@dataclass
class TeamMomentum:
    team_id: int
    team_name: str
    matches: int = 0
    share: float = 0.0  # avg share of match time with momentum
    spells_per_match: float = 0.0
    avg_spell_minutes: float = 0.0
    spell_conversion: float = 0.0  # own spells that ended in a goal
    goals_in_spells_pct: float = 0.0  # own goals scored during own spells
    xg_per_spell: float = 0.0
    rival_spells_per_match: float = 0.0
    rival_spell_conversion: float = 0.0  # rival spells that ended in a goal against
    goals_against_in_rival_spells_pct: float = 0.0


# (match_id, team_id) -> values for that team in that match.
TeamKey = tuple[int, int]


def goal_minutes_by_team(session: Session, match_ids: list[int]) -> dict[TeamKey, list[float]]:
    rows = session.execute(
        select(MatchEvent).where(
            MatchEvent.match_id.in_(match_ids), MatchEvent.event_type == "GOAL"
        )
    ).scalars()
    goals: dict[TeamKey, list[float]] = defaultdict(list)
    for e in rows:
        # Own goals are filed under the scoring team by the provider already.
        goals[(e.match_id, e.team_id)].append(timeline_minute(e.minute, e.extra_minute))
    return goals


def shot_xg_by_team(
    session: Session, match_ids: list[int]
) -> dict[TeamKey, list[tuple[float, float]]]:
    """(timeline minute, xG) of every shot."""
    rows = session.execute(select(MatchShot).where(MatchShot.match_id.in_(match_ids))).scalars()
    shots: dict[TeamKey, list[tuple[float, float]]] = defaultdict(list)
    for s in rows:
        shots[(s.match_id, s.team_id)].append(
            (timeline_minute(s.minute, s.added_time), float(s.xg or 0))
        )
    return shots


def match_sides(
    match: Match,
    curve_points: list[list[float]],
    goals: dict[TeamKey, list[float]],
    shots: dict[TeamKey, list[tuple[float, float]]],
) -> dict[int, MatchMomentumSummary]:
    """Per-team momentum summary for one match, keyed by team id."""
    return {
        team_id: summarize_side(
            oriented(curve_points, home=team_id == match.home_team_id),
            goals.get((match.id, team_id), []),
            shots.get((match.id, team_id), []),
        )
        for team_id in (match.home_team_id, match.away_team_id)
    }


def build_team_momentum(
    session: Session, source: str, league_source_id: str, season_year: int
) -> list[TeamMomentum]:
    matches = get_finished_matches(session, source, league_source_id, season_year)
    by_id = {m.id: m for m in matches}
    curves = {
        row.match_id: row.points
        for row in session.execute(
            select(MatchMomentum).where(MatchMomentum.match_id.in_(by_id))
        ).scalars()
    }
    goals = goal_minutes_by_team(session, list(curves))
    shots = shot_xg_by_team(session, list(curves))

    teams: dict[int, TeamMomentum] = {}
    acc: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for match_id, points in curves.items():
        m = by_id[match_id]
        sides = match_sides(m, points, goals, shots)
        pairs = ((m.home_team_id, m.away_team_id), (m.away_team_id, m.home_team_id))
        for team_id, rival_id in pairs:
            name = m.home_team.name if team_id == m.home_team_id else m.away_team.name
            t = teams.setdefault(team_id, TeamMomentum(team_id=team_id, team_name=name))
            own, rival = sides[team_id], sides[rival_id]
            a = acc[team_id]
            t.matches += 1
            a["share"] += own.share
            a["spells"] += len(own.spells)
            a["spell_minutes"] += sum(s.minutes for s in own.spells)
            a["converted"] += own.spells_converted
            a["goals"] += own.goals
            a["goals_in_spells"] += own.goals_in_spells
            a["xg_in_spells"] += own.xg_in_spells
            a["rival_spells"] += len(rival.spells)
            a["rival_converted"] += rival.spells_converted
            a["conceded"] += rival.goals
            a["conceded_in_rival_spells"] += rival.goals_in_spells

    ratio = lambda num, den: round(num / den, 3) if den else 0.0  # noqa: E731
    for t in teams.values():
        a, n = acc[t.team_id], t.matches
        t.share = ratio(a["share"], n)
        t.spells_per_match = ratio(a["spells"], n)
        t.avg_spell_minutes = round(a["spell_minutes"] / a["spells"], 1) if a["spells"] else 0.0
        t.spell_conversion = ratio(a["converted"], a["spells"])
        t.goals_in_spells_pct = ratio(a["goals_in_spells"], a["goals"])
        t.xg_per_spell = ratio(a["xg_in_spells"], a["spells"])
        t.rival_spells_per_match = ratio(a["rival_spells"], n)
        t.rival_spell_conversion = ratio(a["rival_converted"], a["rival_spells"])
        t.goals_against_in_rival_spells_pct = ratio(a["conceded_in_rival_spells"], a["conceded"])
    return sorted(teams.values(), key=lambda t: -t.share)
