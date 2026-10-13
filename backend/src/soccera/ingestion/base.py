"""
The contract every data source must implement. Sync jobs (ingestion/sync/)
and storage code depend only on this interface and on ingestion.domain
models — never on a specific provider. Swapping API-Football for the
Costa Rican League scraper means writing one new class here, nothing else.
"""

from abc import ABC, abstractmethod
from datetime import date

from soccera.ingestion.domain import (
    DomainLeagueWithSeasons,
    DomainMatch,
    DomainMatchEvent,
    DomainMatchStatistic,
    DomainPlayer,
    DomainPlayerMatchStat,
    DomainSeason,
    DomainTeam,
)


class DataSourceAdapter(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Stable identifier stored in each row's `source` column, e.g. "api_football"."""

    @abstractmethod
    def get_leagues(self, country: str | None = None) -> list[DomainLeagueWithSeasons]:
        ...

    @abstractmethod
    def get_seasons(self, league_source_id: str) -> list[DomainSeason]:
        ...

    @abstractmethod
    def get_teams(self, league_source_id: str, season_year: int) -> list[DomainTeam]:
        ...

    @abstractmethod
    def get_players(self, team_source_id: str, season_year: int) -> list[DomainPlayer]:
        ...

    @abstractmethod
    def get_fixtures(
        self,
        league_source_id: str,
        season_year: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[DomainMatch]:
        """Scheduled/historical fixtures for a league+season, optionally bounded by date."""

    @abstractmethod
    def get_live_fixtures(self) -> list[DomainMatch]:
        ...

    @abstractmethod
    def get_fixture_events(self, match_source_id: str) -> list[DomainMatchEvent]:
        ...

    @abstractmethod
    def get_fixture_statistics(self, match_source_id: str) -> list[DomainMatchStatistic]:
        ...

    def get_fixture_player_stats(self, match_source_id: str) -> list[DomainPlayerMatchStat]:
        """Lineups + per-player stat lines for a match. Optional: providers
        without player-level data keep this default and sync simply skips it."""
        return []
