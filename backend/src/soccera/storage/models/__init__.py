"""
Importing every model module here ensures SQLAlchemy's declarative registry
can resolve the string-based relationship() references between them
(e.g. Season -> "Match") regardless of which module is imported first.
"""

from soccera.storage.models.base import Base
from soccera.storage.models.ingestion_run import IngestionRun
from soccera.storage.models.league import League
from soccera.storage.models.match import Match
from soccera.storage.models.match_event import MatchEvent
from soccera.storage.models.match_statistic import MatchStatistic
from soccera.storage.models.player import Player
from soccera.storage.models.prediction import Prediction
from soccera.storage.models.season import Season
from soccera.storage.models.team import Team
from soccera.storage.models.team_player import TeamPlayer
from soccera.storage.models.venue import Venue

__all__ = [
    "Base",
    "League",
    "Season",
    "Venue",
    "Team",
    "Player",
    "TeamPlayer",
    "Match",
    "MatchStatistic",
    "MatchEvent",
    "Prediction",
    "IngestionRun",
]
