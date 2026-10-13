"""
Single-match report: summary, event timeline, side-by-side stat comparison,
and a "key points" note per team built by comparing that team's numbers in
THIS match against its own season averages (from match_stats.py) — so the
report flags real over/under-performance instead of just echoing raw
numbers.
"""

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.analytics.match_stats import build_match_stat_averages
from soccera.storage.models.match_event import MatchEvent
from soccera.storage.models.match_statistic import MatchStatistic
from soccera.storage.repositories import MatchRepository

# (stat_type, label) — the stats worth flagging when they deviate a lot
# from a team's season average. There are ~30 stat_types total; most are
# too noisy match-to-match to be a meaningful "strength/weakness" signal.
SIGNAL_STATS = [
    ("ballPossession", "posesión"),
    ("totalShotsOnGoal", "tiros"),
    ("expectedGoals", "xG"),
    ("cornerKicks", "corners"),
    ("fouls", "faltas"),
]

DEVIATION_THRESHOLD = 0.25  # flag stats at least 25% off the team's season average


@dataclass
class MatchEventEntry:
    minute: int
    extra_minute: int | None
    event_type: str
    event_detail: str | None
    team_name: str


@dataclass
class StatComparison:
    stat_type: str
    home_value: float | None
    away_value: float | None


@dataclass
class TeamInsight:
    team_name: str
    notes: list[str] = field(default_factory=list)


@dataclass
class MatchReport:
    match_source_id: str
    round: str | None
    match_date: datetime
    status: str
    home_team: str
    away_team: str
    home_score: int | None
    away_score: int | None
    home_score_ht: int | None
    away_score_ht: int | None
    events: list[MatchEventEntry] = field(default_factory=list)
    stat_comparison: list[StatComparison] = field(default_factory=list)
    home_insight: TeamInsight | None = None
    away_insight: TeamInsight | None = None


def _build_insight(
    team_name: str,
    match_values: dict[str, float],
    season_averages: dict[str, float],
    goals_scored: int | None,
) -> TeamInsight:
    notes = []
    for key, label in SIGNAL_STATS:
        match_value = match_values.get(key)
        season_avg = season_averages.get(key)
        if match_value is None or not season_avg:
            continue
        deviation = (match_value - season_avg) / season_avg
        if abs(deviation) >= DEVIATION_THRESHOLD:
            direction = "por encima" if deviation > 0 else "por debajo"
            notes.append(
                f"{label.capitalize()}: {match_value:.1f} vs su promedio de temporada "
                f"{season_avg:.1f} ({deviation:+.0%}, {direction})"
            )

    xg = match_values.get("expectedGoals")
    if xg is not None and goals_scored is not None:
        diff = goals_scored - xg
        if diff >= 1:
            notes.append(f"Clínico de cara al arco: {goals_scored} goles con {xg:.2f} xG esperados.")
        elif diff <= -1:
            notes.append(f"Desperdició ocasiones: {goals_scored} goles con {xg:.2f} xG esperados.")

    return TeamInsight(team_name=team_name, notes=notes)


def build_match_report(session: Session, source: str, match_source_id: str) -> MatchReport:
    match = MatchRepository(session).get_by_source(source, match_source_id)
    if match is None:
        raise ValueError(f"Match {match_source_id!r} not found for source {source!r}")

    team_names = {match.home_team_id: match.home_team.name, match.away_team_id: match.away_team.name}

    events_raw = session.execute(
        select(MatchEvent).where(MatchEvent.match_id == match.id).order_by(MatchEvent.minute)
    ).scalars()
    events = [
        MatchEventEntry(
            minute=e.minute,
            extra_minute=e.extra_minute,
            event_type=e.event_type,
            event_detail=e.event_detail,
            team_name=team_names.get(e.team_id, "?"),
        )
        for e in events_raw
    ]

    stats_raw = session.execute(
        select(MatchStatistic).where(MatchStatistic.match_id == match.id)
    ).scalars()
    home_values: dict[str, float] = {}
    away_values: dict[str, float] = {}
    stat_types: set[str] = set()
    for s in stats_raw:
        if s.stat_value is None:
            continue
        value = float(s.stat_value)
        stat_types.add(s.stat_type)
        if s.team_id == match.home_team_id:
            home_values[s.stat_type] = value
        elif s.team_id == match.away_team_id:
            away_values[s.stat_type] = value

    stat_comparison = [
        StatComparison(stat_type=st, home_value=home_values.get(st), away_value=away_values.get(st))
        for st in sorted(stat_types)
    ]

    season_teams = build_match_stat_averages(session, source, match.league.source_id, match.season.year)
    season_by_team = {t.team_id: t.averages for t in season_teams}

    home_insight = _build_insight(
        match.home_team.name, home_values, season_by_team.get(match.home_team_id, {}), match.home_score
    )
    away_insight = _build_insight(
        match.away_team.name, away_values, season_by_team.get(match.away_team_id, {}), match.away_score
    )

    return MatchReport(
        match_source_id=match_source_id,
        round=match.round,
        match_date=match.match_date,
        status=match.status,
        home_team=match.home_team.name,
        away_team=match.away_team.name,
        home_score=match.home_score,
        away_score=match.away_score,
        home_score_ht=match.home_score_ht,
        away_score_ht=match.away_score_ht,
        events=events,
        stat_comparison=stat_comparison,
        home_insight=home_insight,
        away_insight=away_insight,
    )
