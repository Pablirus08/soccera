from collections import defaultdict
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from soccera.analytics.common import get_finished_matches, get_league_and_season
from soccera.storage.models.match import Match
from soccera.storage.models.match_player_stat import MatchPlayerStat

# Per-match stats summed into season totals (provider stat keys). Sofascore
# omits zero-valued stats from a stat line, so a missing key counts as 0.
SUMMED_STATS = (
    "goals",
    "goalAssist",
    "expectedGoals",
    "expectedAssists",
    "onTargetScoringAttempt",
    "totalShots",
    "keyPass",
    "bigChanceCreated",
    "accuratePass",
    "totalPass",
    "wonTackle",
    "interceptionWon",
    "totalClearance",
    "duelWon",
    "saves",
)

# Strength of the prior in the adjusted rating, in full matches (90'): a
# player's level is pulled toward their position's average as if they had
# also played this many average games. Small samples move little; a full
# season of consistent performances dominates it.
PRIOR_FULL_MATCHES = 5.0


@dataclass
class PlayerSeasonStats:
    player_id: int
    name: str
    team_name: str
    position: str | None
    matches: int = 0
    starts: int = 0
    minutes: int = 0
    rating: float | None = None  # plain mean of match ratings (Sofascore-style)
    adjusted_rating: float | None = None  # minutes-weighted, shrunk to position mean
    participation: float = 0.0  # share of the team's available minutes played
    clean_sheets: int = 0
    totals: dict[str, float] = field(default_factory=dict)


@dataclass
class _RatingSums:
    ratings: list[float] = field(default_factory=list)
    weighted: float = 0.0
    weight: float = 0.0


def match_weight(minutes: int | None) -> float:
    """A rating's weight: share of a full match played (cameos count little)."""
    return min(minutes or 0, 90) / 90


def shrink_rating(
    weighted_sum: float, weight: float, prior: float, k: float = PRIOR_FULL_MATCHES
) -> float:
    """Bayesian average: the player's weighted mean pulled toward `prior`
    as if k extra full matches at the prior had been played."""
    return (weighted_sum + k * prior) / (weight + k)


def build_player_season_stats(
    session: Session,
    source: str,
    league_source_id: str,
    season_year: int,
    min_minutes: int = 0,
    min_participation: float = 0.0,
) -> list[PlayerSeasonStats]:
    """
    Season aggregates per player, ranked by `adjusted_rating` so a couple of
    great cameos can't outrank a season of solid starts:

        adjusted = (Σ rating·w + k·position_mean) / (Σ w + k)

    where w is the share of 90' played in each match and k = PRIOR_FULL_MATCHES.
    `min_participation` (0-1) keeps only players who played at least that
    share of their team's minutes so far; `min_minutes` is an absolute floor.
    A clean sheet counts for a goalkeeper who played 60+ minutes of a match
    the opponent didn't score in.
    """
    league, season = get_league_and_season(session, source, league_source_id, season_year)
    lines = session.execute(
        select(MatchPlayerStat)
        .join(Match, Match.id == MatchPlayerStat.match_id)
        .where(
            Match.league_id == league.id,
            Match.season_id == season.id,
            Match.status == "FINISHED",
        )
        .options(
            joinedload(MatchPlayerStat.player),
            joinedload(MatchPlayerStat.team),
            joinedload(MatchPlayerStat.match),
        )
    ).scalars()

    team_matches: dict[int, int] = defaultdict(int)
    for m in get_finished_matches(session, source, league_source_id, season_year):
        team_matches[m.home_team_id] += 1
        team_matches[m.away_team_id] += 1

    by_player: dict[int, PlayerSeasonStats] = {}
    team_of: dict[int, int] = {}
    sums: dict[int, _RatingSums] = defaultdict(_RatingSums)
    position_sums: dict[str | None, _RatingSums] = defaultdict(_RatingSums)
    for line in lines:
        agg = by_player.get(line.player_id)
        if agg is None:
            agg = by_player[line.player_id] = PlayerSeasonStats(
                player_id=line.player_id,
                name=line.player.name,
                team_name=line.team.name,
                position=line.player.position or line.position,
                totals=dict.fromkeys(SUMMED_STATS, 0.0),
            )
            team_of[line.player_id] = line.team_id
        agg.matches += 1
        agg.starts += int(line.is_starter)
        agg.minutes += line.minutes_played or 0
        for key in SUMMED_STATS:
            agg.totals[key] += float(line.stats.get(key, 0) or 0)

        if line.rating is not None:
            rating, weight = float(line.rating), match_weight(line.minutes_played)
            for bucket in (sums[line.player_id], position_sums[agg.position]):
                bucket.ratings.append(rating)
                bucket.weighted += rating * weight
                bucket.weight += weight

        if agg.position == "Goalkeeper" and (line.minutes_played or 0) >= 60:
            m = line.match
            conceded = m.away_score if line.team_id == m.home_team_id else m.home_score
            if conceded == 0:
                agg.clean_sheets += 1

    position_mean = {
        pos: s.weighted / s.weight for pos, s in position_sums.items() if s.weight > 0
    }

    result = []
    for player_id, agg in by_player.items():
        available = team_matches.get(team_of[player_id], 0) * 90
        agg.participation = round(agg.minutes / available, 3) if available else 0.0
        if agg.minutes < min_minutes or agg.participation < min_participation:
            continue

        s = sums[player_id]
        if s.ratings:
            agg.rating = round(sum(s.ratings) / len(s.ratings), 2)
            prior = position_mean.get(agg.position, agg.rating)
            agg.adjusted_rating = round(shrink_rating(s.weighted, s.weight, prior), 2)
        agg.totals = {k: round(v, 2) for k, v in agg.totals.items()}
        result.append(agg)

    result.sort(key=lambda p: (p.adjusted_rating is None, -(p.adjusted_rating or 0), -p.minutes))
    return result
