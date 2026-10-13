import time
from datetime import date

from soccera.ingestion.base import DataSourceAdapter
from soccera.ingestion.domain import (
    DomainLeague,
    DomainLeagueWithSeasons,
    DomainMatch,
    DomainMatchEvent,
    DomainMatchStatistic,
    DomainMomentum,
    DomainPlayer,
    DomainPlayerMatchStat,
    DomainSeason,
    DomainShot,
    DomainTeam,
    DomainTeamHeatmap,
)
from soccera.ingestion.providers.costa_rica.client import SofascoreClient, SofascoreError
from soccera.ingestion.providers.costa_rica.mappers import (
    map_fixture,
    map_fixture_event,
    map_fixture_statistics,
    map_heatmap,
    map_lineup_player,
    map_momentum,
    map_player,
    map_shot,
    map_team,
    season_year_from_sofascore_year,
)
from soccera.ingestion.providers.costa_rica.schemas import (
    RawEventEntry,
    RawGraphPoint,
    RawHeatmap,
    RawIncidentEntry,
    RawLineupSide,
    RawShot,
    RawSquadPlayer,
    RawStatisticPeriod,
    RawTeamRef,
)
from soccera.logging import get_logger

logger = get_logger(__name__)

# Season lists and fixture-list pages are requested several times within one
# backfill (teams, then fixtures). Short enough that live polling (60s) still
# sees fresh pages on every poll.
LIST_CACHE_SECONDS = 30.0

# Sofascore tracks Costa Rica's Primera Division as two separate
# tournaments (Apertura/Clausura), each with its own unique-tournament id.
# There's no API-Football-style single "league" — these ARE the leagues.
LEAGUES: dict[str, dict[str, str]] = {
    "11535": {"name": "Primera Division, Apertura", "country": "Costa Rica"},
    "11542": {"name": "Primera Division, Clausura", "country": "Costa Rica"},
}


class SofascoreAdapter(DataSourceAdapter):
    """
    DataSourceAdapter for Costa Rica's Primera Division, backed by
    Sofascore's public API. Unlike API-Football's free plan, this has no
    season restriction — it can reach the current, in-progress season.

    Requests impersonate a Chrome TLS fingerprint to get past Sofascore's
    anti-bot protection (see SofascoreClient) and are throttled. Avoid
    calling it in tight loops; historical.py/live.py already call it at a
    sane granularity.
    """

    def __init__(self, client: SofascoreClient | None = None):
        self._client = client or SofascoreClient()
        self._team_ids: dict[str, tuple[str, str]] = {}
        self._list_cache: dict[str, tuple[float, dict]] = {}

    @property
    def source_name(self) -> str:
        return "sofascore"

    def close(self) -> None:
        self._client.close()

    def _get_or_empty(self, path: str) -> dict:
        """For endpoints where a 404 legitimately means "no data" (e.g. a
        match without statistics). Anything else, like a 403 block, raises."""
        try:
            return self._client.get(path)
        except SofascoreError as exc:
            if exc.code == 404:
                return {}
            raise

    def _get_list(self, path: str) -> dict:
        """GET for season/fixture-list endpoints, memoized for LIST_CACHE_SECONDS."""
        hit = self._list_cache.get(path)
        if hit and time.monotonic() - hit[0] < LIST_CACHE_SECONDS:
            return hit[1]
        data = self._client.get(path)
        self._list_cache[path] = (time.monotonic(), data)
        return data

    def _season_id_for_year(self, league_source_id: str, season_year: int) -> int:
        seasons = self._get_list(f"/unique-tournament/{league_source_id}/seasons")
        for entry in seasons.get("seasons", []):
            if season_year_from_sofascore_year(entry["year"]) == season_year:
                return entry["id"]
        raise ValueError(
            f"No Sofascore season found for league {league_source_id}, year {season_year}"
        )

    def _iter_events(self, league_source_id: str, season_id: int) -> list[dict]:
        """Every event of the season: `last` pages hold played/past fixtures,
        `next` pages the upcoming ones. Deduplicated by id, since a match
        about to kick off can briefly show up in both."""
        events: dict[int, dict] = {}
        for direction in ("last", "next"):
            page = 0
            while True:
                path = (
                    f"/unique-tournament/{league_source_id}/season/{season_id}"
                    f"/events/{direction}/{page}"
                )
                try:
                    data = self._get_list(path)
                except SofascoreError as exc:
                    if exc.code == 404:  # past the last page
                        break
                    raise
                if not data.get("events"):
                    break
                for ev in data["events"]:
                    events[ev["id"]] = ev
                if not data.get("hasNextPage", True):
                    break
                page += 1
        return list(events.values())

    def get_leagues(self, country: str | None = None) -> list[DomainLeagueWithSeasons]:
        result = []
        for league_source_id, meta in LEAGUES.items():
            if country and meta["country"].lower() != country.lower():
                continue
            result.append(
                DomainLeagueWithSeasons(
                    league=DomainLeague(
                        source_id=league_source_id, name=meta["name"], country=meta["country"]
                    ),
                    seasons=self.get_seasons(league_source_id),
                )
            )
        return result

    def get_seasons(self, league_source_id: str) -> list[DomainSeason]:
        seasons_raw = self._get_list(f"/unique-tournament/{league_source_id}/seasons")["seasons"]
        return [
            DomainSeason(
                league_source_id=league_source_id,
                year=season_year_from_sofascore_year(s["year"]),
                is_current=(i == 0),  # Sofascore returns seasons newest-first.
            )
            for i, s in enumerate(seasons_raw)
        ]

    def get_teams(self, league_source_id: str, season_year: int) -> list[DomainTeam]:
        season_id = self._season_id_for_year(league_source_id, season_year)
        events = self._iter_events(league_source_id, season_id)
        seen: dict[str, DomainTeam] = {}
        for ev in events:
            for key in ("homeTeam", "awayTeam"):
                team = map_team(RawTeamRef.model_validate(ev[key]))
                seen[team.source_id] = team
        return list(seen.values())

    def get_players(self, team_source_id: str, season_year: int) -> list[DomainPlayer]:
        # Sofascore only exposes the *current* squad per team, not a
        # season-specific historical roster — season_year is accepted for
        # interface compatibility but doesn't filter anything here.
        data = self._get_or_empty(f"/team/{team_source_id}/players")
        return [
            map_player(RawSquadPlayer.model_validate(entry["player"]))
            for entry in data.get("players", [])
        ]

    def get_fixtures(
        self,
        league_source_id: str,
        season_year: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[DomainMatch]:
        season_id = self._season_id_for_year(league_source_id, season_year)
        events = self._iter_events(league_source_id, season_id)
        fixtures = [
            map_fixture(RawEventEntry.model_validate(ev), league_source_id, season_year)
            for ev in events
        ]
        if date_from:
            fixtures = [f for f in fixtures if f.match_date.date() >= date_from]
        if date_to:
            fixtures = [f for f in fixtures if f.match_date.date() <= date_to]
        return fixtures

    def get_live_fixtures(self) -> list[DomainMatch]:
        live: list[DomainMatch] = []
        for league_source_id in LEAGUES:
            seasons_raw = self._get_list(f"/unique-tournament/{league_source_id}/seasons")[
                "seasons"
            ]
            if not seasons_raw:
                continue
            current = seasons_raw[0]
            season_year = season_year_from_sofascore_year(current["year"])
            for ev in self._iter_events(league_source_id, current["id"]):
                raw = RawEventEntry.model_validate(ev)
                if raw.status.type == "inprogress":
                    live.append(map_fixture(raw, league_source_id, season_year))
        return live

    def _match_team_ids(self, match_source_id: str) -> tuple[str, str]:
        """(home, away) team ids. Cached because events and statistics both
        need them and a match's teams never change — saves one call per match."""
        if match_source_id not in self._team_ids:
            event = self._client.get(f"/event/{match_source_id}")["event"]
            self._team_ids[match_source_id] = (
                str(event["homeTeam"]["id"]),
                str(event["awayTeam"]["id"]),
            )
        return self._team_ids[match_source_id]

    def get_fixture_events(self, match_source_id: str) -> list[DomainMatchEvent]:
        incidents = self._get_or_empty(f"/event/{match_source_id}/incidents")
        home_id, away_id = self._match_team_ids(match_source_id)

        results = []
        for raw in incidents.get("incidents", []):
            entry = RawIncidentEntry.model_validate(raw)
            mapped = map_fixture_event(entry, match_source_id, home_id, away_id)
            if mapped is not None:
                results.append(mapped)
        return results

    def get_fixture_statistics(self, match_source_id: str) -> list[DomainMatchStatistic]:
        stats = self._get_or_empty(f"/event/{match_source_id}/statistics")
        home_id, away_id = self._match_team_ids(match_source_id)

        periods = [RawStatisticPeriod.model_validate(p) for p in stats.get("statistics", [])]
        return map_fixture_statistics(periods, match_source_id, home_id, away_id)

    def get_fixture_shots(self, match_source_id: str) -> list[DomainShot]:
        data = self._get_or_empty(f"/event/{match_source_id}/shotmap")
        if not data:
            return []
        home_id, away_id = self._match_team_ids(match_source_id)
        return [
            map_shot(RawShot.model_validate(s), match_source_id, home_id, away_id)
            for s in data.get("shotmap", [])
        ]

    def get_fixture_momentum(self, match_source_id: str) -> DomainMomentum | None:
        data = self._get_or_empty(f"/event/{match_source_id}/graph")
        points = [RawGraphPoint.model_validate(p) for p in data.get("graphPoints", [])]
        return map_momentum(points, match_source_id) if points else None

    def get_fixture_heatmaps(self, match_source_id: str) -> list[DomainTeamHeatmap]:
        heatmaps = []
        for team_id in self._match_team_ids(match_source_id):
            data = self._get_or_empty(f"/event/{match_source_id}/heatmap/{team_id}")
            if data:
                heatmaps.append(
                    map_heatmap(RawHeatmap.model_validate(data), match_source_id, team_id)
                )
        return heatmaps

    def get_fixture_player_stats(self, match_source_id: str) -> list[DomainPlayerMatchStat]:
        lineups = self._get_or_empty(f"/event/{match_source_id}/lineups")
        if not lineups:
            return []
        home_id, away_id = self._match_team_ids(match_source_id)

        results = []
        for side_key, team_id in (("home", home_id), ("away", away_id)):
            side = RawLineupSide.model_validate(lineups.get(side_key, {}))
            for raw in side.players:
                results.append(map_lineup_player(raw, match_source_id, team_id))
        return results
