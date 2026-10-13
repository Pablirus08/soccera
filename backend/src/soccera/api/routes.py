from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from soccera.analytics.discipline import build_discipline
from soccera.analytics.goals import build_goal_stats
from soccera.analytics.leagues import list_leagues
from soccera.analytics.match_report import build_match_report
from soccera.analytics.match_stats import build_match_stat_averages
from soccera.analytics.matches import build_match_list
from soccera.analytics.standings import build_standings
from soccera.api.dependencies import get_db
from soccera.api.schemas import (
    GoalStatsOut,
    LeagueOut,
    MatchListItemOut,
    MatchReportOut,
    StandingsOut,
    TeamDisciplineOut,
    TeamStatAveragesOut,
)

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


@router.get("/matches/{match_source_id}", response_model=MatchReportOut)
def get_match(match_source_id: str, source: str = "sofascore", db: Session = Depends(get_db)):
    try:
        return build_match_report(db, source, match_source_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
