"""
Shot maps, heatmaps, match timelines and head-to-head comparisons, built
from match_shots / match_momentum / match_team_heatmaps.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from soccera.analytics.common import get_finished_matches
from soccera.analytics.momentum import (
    MatchMomentumSummary,
    Spell,
    goal_minutes_by_team,
    match_sides,
    shot_xg_by_team,
    timeline_minute,
)
from soccera.models.poisson import MatchResult, PoissonModel
from soccera.storage.models.match import Match
from soccera.storage.models.match_event import MatchEvent
from soccera.storage.models.match_visuals import (
    HEATMAP_COLS,
    HEATMAP_ROWS,
    MatchMomentum,
    MatchShot,
    MatchTeamHeatmap,
)
from soccera.storage.models.team import Team
from soccera.storage.repositories import MatchRepository

# Shots from closer than this (in pitch-length %) are inside the box:
# 16.5 m of a ~105 m pitch.
BOX_DEPTH_PCT = 15.7


@dataclass
class ShotPoint:
    match_source_id: str
    minute: int
    added_time: int | None
    x: float
    y: float
    shot_type: str
    situation: str | None
    body_part: str | None
    xg: float | None
    xgot: float | None
    player_name: str | None
    team_name: str
    opponent_name: str


@dataclass
class ShotSummary:
    shots: int = 0
    goals: int = 0
    on_target: int = 0
    xg: float = 0.0
    inside_box_pct: float = 0.0
    xg_per_shot: float = 0.0


@dataclass
class Heatmap:
    cols: int
    rows: int
    grid: list[int]
    matches: int


@dataclass
class TeamVisuals:
    team_id: int
    team_name: str
    shots_for: list[ShotPoint]
    shots_against: list[ShotPoint]
    summary_for: ShotSummary
    summary_against: ShotSummary
    heatmap: Heatmap


def summarize_shots(shots: list[ShotPoint]) -> ShotSummary:
    n = len(shots)
    xg = sum(s.xg or 0 for s in shots)
    return ShotSummary(
        shots=n,
        goals=sum(s.shot_type == "goal" for s in shots),
        on_target=sum(s.shot_type in ("goal", "save") for s in shots),
        xg=round(xg, 2),
        inside_box_pct=round(sum(s.x <= BOX_DEPTH_PCT for s in shots) / n, 3) if n else 0.0,
        xg_per_shot=round(xg / n, 3) if n else 0.0,
    )


def _shot_point(s: MatchShot, match: Match, team_names: dict[int, str]) -> ShotPoint:
    opponent = match.away_team_id if s.team_id == match.home_team_id else match.home_team_id
    return ShotPoint(
        match_source_id=match.source_id,
        minute=s.minute,
        added_time=s.added_time,
        x=float(s.x),
        y=float(s.y),
        shot_type=s.shot_type,
        situation=s.situation,
        body_part=s.body_part,
        xg=float(s.xg) if s.xg is not None else None,
        xgot=float(s.xgot) if s.xgot is not None else None,
        player_name=s.player.name if s.player else None,
        team_name=team_names[s.team_id],
        opponent_name=team_names[opponent],
    )


def sum_heatmaps(grids: list[list[int]]) -> list[int]:
    total = [0] * (HEATMAP_ROWS * HEATMAP_COLS)
    for g in grids:
        for i, v in enumerate(g):
            total[i] += v
    return total


def build_team_visuals(
    session: Session, source: str, league_source_id: str, season_year: int, team_id: int
) -> TeamVisuals:
    matches = [
        m
        for m in get_finished_matches(session, source, league_source_id, season_year)
        if team_id in (m.home_team_id, m.away_team_id)
    ]
    by_id = {m.id: m for m in matches}
    team_names = {m.home_team_id: m.home_team.name for m in matches}
    team_names.update({m.away_team_id: m.away_team.name for m in matches})
    if team_id not in team_names:
        team = session.get(Team, team_id)
        if team is None:
            raise ValueError(f"Team {team_id} not found")
        team_names[team_id] = team.name

    shots = session.execute(
        select(MatchShot)
        .where(MatchShot.match_id.in_(by_id))
        .options(joinedload(MatchShot.player))
    ).scalars()
    shots_for, shots_against = [], []
    for s in shots:
        point = _shot_point(s, by_id[s.match_id], team_names)
        (shots_for if s.team_id == team_id else shots_against).append(point)

    grids = session.execute(
        select(MatchTeamHeatmap.grid).where(
            MatchTeamHeatmap.match_id.in_(by_id), MatchTeamHeatmap.team_id == team_id
        )
    ).scalars().all()

    return TeamVisuals(
        team_id=team_id,
        team_name=team_names[team_id],
        shots_for=shots_for,
        shots_against=shots_against,
        summary_for=summarize_shots(shots_for),
        summary_against=summarize_shots(shots_against),
        heatmap=Heatmap(HEATMAP_COLS, HEATMAP_ROWS, sum_heatmaps(list(grids)), len(grids)),
    )


@dataclass
class GoalMark:
    minute: float  # on the momentum timeline
    label: str  # e.g. "45+2'"
    team_name: str
    player_name: str | None


@dataclass
class SideMomentum:
    team_name: str
    spells: list[Spell]
    spells_converted: int
    share: float
    xg_in_spells: float


@dataclass
class MatchVisuals:
    source_id: str
    round: str | None
    match_date: datetime
    status: str
    home_team: str
    away_team: str
    home_score: int | None
    away_score: int | None
    momentum: list[list[float]]  # [[minute, value]], value > 0 = home pressing
    goals: list[GoalMark]
    home_momentum: SideMomentum | None
    away_momentum: SideMomentum | None
    shots: list[ShotPoint]
    home_heatmap: Heatmap | None
    away_heatmap: Heatmap | None
    xg_home: float = 0.0
    xg_away: float = 0.0


def _side(name: str, summary: MatchMomentumSummary) -> SideMomentum:
    return SideMomentum(
        team_name=name,
        spells=summary.spells,
        spells_converted=summary.spells_converted,
        share=round(summary.share, 3),
        xg_in_spells=round(summary.xg_in_spells, 2),
    )


def build_match_visuals(session: Session, source: str, match_source_id: str) -> MatchVisuals:
    match = MatchRepository(session).get_by_source(source, match_source_id)
    if match is None:
        raise ValueError(f"Match {match_source_id!r} not found for source {source!r}")
    names = {match.home_team_id: match.home_team.name, match.away_team_id: match.away_team.name}

    curve = session.execute(
        select(MatchMomentum.points).where(MatchMomentum.match_id == match.id)
    ).scalar_one_or_none()
    shots = [
        _shot_point(s, match, names)
        for s in session.execute(
            select(MatchShot)
            .where(MatchShot.match_id == match.id)
            .options(joinedload(MatchShot.player))
            .order_by(MatchShot.minute)
        ).scalars()
    ]
    heatmaps = {
        h.team_id: Heatmap(HEATMAP_COLS, HEATMAP_ROWS, h.grid, 1)
        for h in session.execute(
            select(MatchTeamHeatmap).where(MatchTeamHeatmap.match_id == match.id)
        ).scalars()
    }

    goal_events = session.execute(
        select(MatchEvent)
        .where(MatchEvent.match_id == match.id, MatchEvent.event_type == "GOAL")
        .options(joinedload(MatchEvent.player))
        .order_by(MatchEvent.minute)
    ).scalars()
    goals = [
        GoalMark(
            minute=timeline_minute(e.minute, e.extra_minute),
            label=f"{e.minute}+{e.extra_minute}'" if e.extra_minute else f"{e.minute}'",
            team_name=names.get(e.team_id, "?"),
            player_name=e.player.name if e.player else None,
        )
        for e in goal_events
    ]

    home_side = away_side = None
    if curve:
        sides = match_sides(
            match,
            curve,
            goal_minutes_by_team(session, [match.id]),
            shot_xg_by_team(session, [match.id]),
        )
        home_side = _side(names[match.home_team_id], sides[match.home_team_id])
        away_side = _side(names[match.away_team_id], sides[match.away_team_id])

    return MatchVisuals(
        source_id=match.source_id,
        round=match.round,
        match_date=match.match_date,
        status=match.status,
        home_team=names[match.home_team_id],
        away_team=names[match.away_team_id],
        home_score=match.home_score,
        away_score=match.away_score,
        momentum=curve or [],
        goals=goals,
        home_momentum=home_side,
        away_momentum=away_side,
        shots=shots,
        home_heatmap=heatmaps.get(match.home_team_id),
        away_heatmap=heatmaps.get(match.away_team_id),
        xg_home=round(sum(s.xg or 0 for s in shots if s.team_name == names[match.home_team_id]), 2),
        xg_away=round(sum(s.xg or 0 for s in shots if s.team_name == names[match.away_team_id]), 2),
    )


@dataclass
class H2HMatch:
    source_id: str
    match_date: datetime
    tournament: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int


@dataclass
class H2HPrediction:
    home_team: str
    away_team: str
    home_win: float
    draw: float
    away_win: float
    expected_home_goals: float
    expected_away_goals: float


@dataclass
class HeadToHead:
    team_a: str
    team_b: str
    played: int
    a_wins: int
    draws: int
    b_wins: int
    a_goals: int
    b_goals: int
    matches: list[H2HMatch]
    a_home: H2HPrediction
    b_home: H2HPrediction


def build_head_to_head(session: Session, source: str, team_a_id: int, team_b_id: int) -> HeadToHead:
    """Every finished meeting since data starts (all tournaments) plus the
    Poisson model's forecast with each side at home."""
    team_a, team_b = session.get(Team, team_a_id), session.get(Team, team_b_id)
    if team_a is None or team_b is None:
        raise ValueError("Unknown team id")

    history = MatchRepository(session).get_finished(source)
    model = PoissonModel.fit(
        [MatchResult(m.home_team_id, m.away_team_id, m.home_score, m.away_score) for m in history]
    )
    meetings = session.execute(
        select(Match)
        .where(
            Match.source == source,
            Match.status == "FINISHED",
            or_(
                (Match.home_team_id == team_a_id) & (Match.away_team_id == team_b_id),
                (Match.home_team_id == team_b_id) & (Match.away_team_id == team_a_id),
            ),
        )
        .order_by(Match.match_date.desc())
    ).scalars().all()

    a_wins = draws = b_wins = a_goals = b_goals = 0
    rows = []
    for m in meetings:
        a_score = m.home_score if m.home_team_id == team_a_id else m.away_score
        b_score = m.away_score if m.home_team_id == team_a_id else m.home_score
        a_goals += a_score
        b_goals += b_score
        if a_score > b_score:
            a_wins += 1
        elif a_score < b_score:
            b_wins += 1
        else:
            draws += 1
        stage = "Apertura" if "Apertura" in m.league.name else "Clausura"
        rows.append(
            H2HMatch(
                m.source_id, m.match_date, f"{stage} {m.season.year}",
                m.home_team.name, m.away_team.name, m.home_score, m.away_score,
            )
        )

    def forecast(home: Team, away: Team) -> H2HPrediction:
        p = model.predict(home.id, away.id)
        return H2HPrediction(
            home.name, away.name, round(p.home_win, 3), round(p.draw, 3), round(p.away_win, 3),
            round(p.expected_home_goals, 2), round(p.expected_away_goals, 2),
        )

    return HeadToHead(
        team_a=team_a.name,
        team_b=team_b.name,
        played=len(meetings),
        a_wins=a_wins,
        draws=draws,
        b_wins=b_wins,
        a_goals=a_goals,
        b_goals=b_goals,
        matches=rows,
        a_home=forecast(team_a, team_b),
        b_home=forecast(team_b, team_a),
    )

