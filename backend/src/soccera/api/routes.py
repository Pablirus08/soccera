from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from soccera.analytics.discipline import build_discipline
from soccera.analytics.goals import build_goal_stats
from soccera.analytics.leagues import list_leagues
from soccera.analytics.match_report import build_match_report
from soccera.analytics.match_stats import build_match_stat_averages
from soccera.analytics.matches import build_match_list
from soccera.analytics.players import build_player_season_stats
from soccera.analytics.standings import build_standings
from soccera.api.dependencies import get_db
from soccera.api.schemas import (
    GoalStatsOut,
    LeagueOut,
    MatchListItemOut,
    MatchReportOut,
    PlayerSeasonStatsOut,
    StandingsOut,
    SyncResultOut,
    SyncStatusOut,
    TeamDisciplineOut,
    TeamStatAveragesOut,
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


@router.get("/matches/{match_source_id}", response_model=MatchReportOut)
def get_match(match_source_id: str, source: str = "sofascore", db: Session = Depends(get_db)):
    try:
        return build_match_report(db, source, match_source_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
