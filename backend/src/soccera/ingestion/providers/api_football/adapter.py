from datetime import date

from soccera.ingestion.base import DataSourceAdapter
from soccera.ingestion.domain import (
    DomainLeagueWithSeasons,
    DomainMatch,
    DomainMatchEvent,
    DomainMatchStatistic,
    DomainPlayer,
    DomainSeason,
    DomainTeam,
)
from soccera.ingestion.providers.api_football.client import ApiFootballClient
from soccera.ingestion.providers.api_football.mappers import (
    map_fixture,
    map_fixture_event,
    map_fixture_statistics,
    map_league,
    map_player,
    map_team,
)
from soccera.ingestion.providers.api_football.schemas import (
    RawFixtureEntry,
    RawFixtureEventEntry,
    RawFixtureStatisticsEntry,
    RawLeagueEntry,
    RawPlayerEntry,
    RawTeamEntry,
)


class ApiFootballAdapter(DataSourceAdapter):
    """DataSourceAdapter implementation backed by api-sports.io's API-Football v3."""

    def __init__(self, client: ApiFootballClient | None = None):
        self._client = client or ApiFootballClient()

    @property
    def source_name(self) -> str:
        return "api_football"

    def close(self) -> None:
        self._client.close()

    def get_leagues(self, country: str | None = None) -> list[DomainLeagueWithSeasons]:
        params = {"country": country} if country else {}
        raw = self._client.get("leagues", params)
        return [map_league(RawLeagueEntry.model_validate(entry)) for entry in raw]

    def get_seasons(self, league_source_id: str) -> list[DomainSeason]:
        raw = self._client.get("leagues", {"id": league_source_id})
        entries = [map_league(RawLeagueEntry.model_validate(e)) for e in raw]
        return entries[0].seasons if entries else []

    def get_teams(self, league_source_id: str, season_year: int) -> list[DomainTeam]:
        raw = self._client.get("teams", {"league": league_source_id, "season": season_year})
        return [map_team(RawTeamEntry.model_validate(entry)) for entry in raw]

    def get_players(self, team_source_id: str, season_year: int) -> list[DomainPlayer]:
        players: list[DomainPlayer] = []
        page = 1
        while True:
            raw = self._client.get(
                "players", {"team": team_source_id, "season": season_year, "page": page}
            )
            if not raw:
                break
            players.extend(map_player(RawPlayerEntry.model_validate(entry)) for entry in raw)
            if len(raw) < 20:  # API-Football pages at 20 results
                break
            page += 1
        return players

    def get_fixtures(
        self,
        league_source_id: str,
        season_year: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[DomainMatch]:
        params: dict[str, str | int] = {"league": league_source_id, "season": season_year}
        if date_from:
            params["from"] = date_from.isoformat()
        if date_to:
            params["to"] = date_to.isoformat()
        raw = self._client.get("fixtures", params)
        return [map_fixture(RawFixtureEntry.model_validate(entry)) for entry in raw]

    def get_live_fixtures(self) -> list[DomainMatch]:
        raw = self._client.get("fixtures", {"live": "all"})
        return [map_fixture(RawFixtureEntry.model_validate(entry)) for entry in raw]

    def get_fixture_events(self, match_source_id: str) -> list[DomainMatchEvent]:
        raw = self._client.get("fixtures/events", {"fixture": match_source_id})
        return [
            map_fixture_event(RawFixtureEventEntry.model_validate(entry), match_source_id)
            for entry in raw
        ]

    def get_fixture_statistics(self, match_source_id: str) -> list[DomainMatchStatistic]:
        raw = self._client.get("fixtures/statistics", {"fixture": match_source_id})
        stats: list[DomainMatchStatistic] = []
        for entry in raw:
            stats.extend(
                map_fixture_statistics(
                    RawFixtureStatisticsEntry.model_validate(entry), match_source_id
                )
            )
        return stats
