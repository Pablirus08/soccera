from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from soccera.analytics.discipline import build_discipline
from soccera.analytics.goals import build_goal_stats
from soccera.analytics.leagues import list_leagues
from soccera.analytics.match_report import build_match_report
from soccera.analytics.match_stats import build_match_stat_averages
from soccera.analytics.matches import build_match_list
from soccera.analytics.momentum import build_team_momentum
from soccera.analytics.players import build_player_season_stats
from soccera.analytics.predictions import build_predictions
from soccera.analytics.standings import build_standings
from soccera.analytics.team_profiles import build_team_profiles
from soccera.analytics.visuals import (
    build_head_to_head,
    build_match_visuals,
    build_team_visuals,
)
from soccera.api.dependencies import get_db
from soccera.api.schemas import (
    GoalStatsOut,
    HeadToHeadOut,
    LeagueOut,
    MatchListItemOut,
    MatchReportOut,
    MatchVisualsOut,
    PlayerSeasonStatsOut,
    PredictionsOut,
    StandingsOut,
    SyncResultOut,
    SyncStatusOut,
    TeamDisciplineOut,
    TeamMomentumOut,
    TeamProfileOut,
    TeamStatAveragesOut,
    TeamVisualsOut,
)
from soccera.ingestion.providers.costa_rica.adapter import SofascoreAdapter
from soccera.ingestion.providers.costa_rica.client import SofascoreError
from soccera.ingestion.sync.season_sync import (
    SyncInProgressError,
    SyncResult,
    check_sync_status,
    sync_season,
)
from soccera.storage.database import session_scope

router = APIRouter()


@router.get("/leagues", response_model=list[LeagueOut])
def get_leagues(db: Session = Depends(get_db)):
    return list_leagues(db)


@router.get("/standings", response_model=StandingsOut)
def get_standings(league: str, season: int, source: str = "sofascore", db: Session = Depends(get_db)):
    try:
        return build_standings(db, source, league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/goals", response_model=GoalStatsOut)
def get_goals(league: str, season: int, source: str = "sofascore", db: Session = Depends(get_db)):
    try:
        return build_goal_stats(db, source, league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/discipline", response_model=list[TeamDisciplineOut])
def get_discipline(league: str, season: int, source: str = "sofascore", db: Session = Depends(get_db)):
    try:
        return build_discipline(db, source, league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/stats", response_model=list[TeamStatAveragesOut])
def get_stats(league: str, season: int, source: str = "sofascore", db: Session = Depends(get_db)):
    try:
        return build_match_stat_averages(db, source, league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/matches", response_model=list[MatchListItemOut])
def get_matches(league: str, season: int, source: str = "sofascore", db: Session = Depends(get_db)):
    try:
        return build_match_list(db, source, league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/players", response_model=list[PlayerSeasonStatsOut])
def get_players(
    league: str,
    season: int,
    min_minutes: int = 0,
    min_participation: float = Query(0.0, ge=0.0, le=1.0),
    source: str = "sofascore",
    db: Session = Depends(get_db),
):
    """Ranked by adjusted_rating. min_participation: share (0-1) of the team's minutes."""
    try:
        return build_player_season_stats(
            db, source, league, season, min_minutes, min_participation
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/teams/profiles", response_model=list[TeamProfileOut])
def get_team_profiles(
    league: str, season: int, source: str = "sofascore", db: Session = Depends(get_db)
):
    """xG for/against, expected points and shot profile per team."""
    try:
        return build_team_profiles(db, source, league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/momentum", response_model=list[TeamMomentumOut])
def get_momentum(
    league: str, season: int, source: str = "sofascore", db: Session = Depends(get_db)
):
    """Per team: how often and how long it dominates, and how well it (and its
    rivals) turn those spells into goals."""
    try:
        return build_team_momentum(db, source, league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/teams/{team_id}/visuals", response_model=TeamVisualsOut)
def get_team_visuals(
    team_id: int,
    league: str,
    season: int,
    source: str = "sofascore",
    db: Session = Depends(get_db),
):
    """Season shot map (for and against) and touch heatmap for one team."""
    try:
        return build_team_visuals(db, source, league, season, team_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/h2h", response_model=HeadToHeadOut)
def get_head_to_head(
    team_a: int, team_b: int, source: str = "sofascore", db: Session = Depends(get_db)
):
    """All meetings since 2022 plus the model's forecast with each side at home."""
    try:
        return build_head_to_head(db, source, team_a, team_b)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/predictions", response_model=PredictionsOut)
def get_predictions(
    league: str, season: int, source: str = "sofascore", db: Session = Depends(get_db)
):
    """Poisson-model probabilities for the next round, plus team strength ratings."""
    try:
        return build_predictions(db, source, league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sync/status", response_model=SyncStatusOut)
def get_sync_status(
    league: str, season: int, source: str = "sofascore", db: Session = Depends(get_db)
):
    """Database-only freshness check — never calls the data provider."""
    try:
        return check_sync_status(db, source, league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sync", response_model=SyncResultOut)
def post_sync(league: str, season: int, force: bool = False):
    """
    Pulls the latest fixtures and match detail from Sofascore. Unless `force`,
    it first checks the database and returns without any provider call when
    nothing is stale (fixtures_synced == details_synced == 0).
    """
    # Short-lived session for the check only: the sync below can take a while
    # and manages its own per-step sessions.
    try:
        with session_scope() as session:
            status = check_sync_status(session, "sofascore", league, season)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if status.up_to_date and not force:
        return SyncResult(fixtures_synced=0, details_synced=0, status=status)

    adapter = SofascoreAdapter()
    try:
        return sync_season(adapter, league, season)
    except SyncInProgressError as exc:
        raise HTTPException(status_code=409, detail="Ya hay una actualización en curso") from exc
    except SofascoreError as exc:
        detail = "Sofascore bloqueó la solicitud (403)" if exc.code == 403 else str(exc)
        raise HTTPException(status_code=502, detail=detail) from exc
    finally:
        adapter.close()


@router.get("/matches/{match_source_id}/visuals", response_model=MatchVisualsOut)
def get_match_visuals(match_source_id: str, source: str = "sofascore", db: Session = Depends(get_db)):
    """Momentum curve with spells and goals, shots and both teams' heatmaps."""
    try:
        return build_match_visuals(db, source, match_source_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/matches/{match_source_id}", response_model=MatchReportOut)
def get_match(match_source_id: str, source: str = "sofascore", db: Session = Depends(get_db)):
    try:
        return build_match_report(db, source, match_source_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
