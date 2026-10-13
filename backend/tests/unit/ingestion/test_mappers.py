from soccera.ingestion.providers.api_football.mappers import (
    map_fixture,
    map_fixture_event,
    map_fixture_statistics,
    map_league,
)
from soccera.ingestion.providers.api_football.schemas import (
    RawEventPlayer,
    RawEventTeam,
    RawFixtureEntry,
    RawFixtureEventEntry,
    RawFixtureInfo,
    RawFixtureLeague,
    RawFixtureScore,
    RawFixtureScores,
    RawFixtureStatisticsEntry,
    RawFixtureStatus,
    RawFixtureTeamRef,
    RawFixtureTeams,
    RawLeagueEntry,
    RawLeagueInfo,
    RawSeasonInfo,
    RawStatisticValue,
)


def test_map_league_includes_seasons():
    raw = RawLeagueEntry(
        league=RawLeagueInfo(id=39, name="Premier League", country="England", type="League"),
        seasons=[RawSeasonInfo(year=2024, start="2024-08-01", end="2025-05-31", current=True)],
    )

    result = map_league(raw)

    assert result.league.source_id == "39"
    assert result.league.type == "league"
    assert len(result.seasons) == 1
    assert result.seasons[0].year == 2024
    assert result.seasons[0].is_current is True


def test_map_fixture_translates_live_status_code():
    raw = RawFixtureEntry(
        fixture=RawFixtureInfo(
            id=1001,
            date="2024-08-20T15:00:00+00:00",
            status=RawFixtureStatus(short="1H", elapsed=23),
        ),
        league=RawFixtureLeague(id=39, season=2024, round="Regular Season - 1"),
        teams=RawFixtureTeams(home=RawFixtureTeamRef(id=33), away=RawFixtureTeamRef(id=34)),
        goals=RawFixtureScore(home=1, away=0),
        score=RawFixtureScores(halftime=RawFixtureScore(home=1, away=0)),
    )

    result = map_fixture(raw)

    assert result.status == "LIVE"
    assert result.elapsed_minutes == 23
    assert result.home_team_source_id == "33"
    assert result.away_team_source_id == "34"


def test_map_fixture_unmapped_status_defaults_to_scheduled():
    raw = RawFixtureEntry(
        fixture=RawFixtureInfo(
            id=1002,
            date="2024-08-20T15:00:00+00:00",
            status=RawFixtureStatus(short="SOME_NEW_CODE", elapsed=None),
        ),
        league=RawFixtureLeague(id=39, season=2024),
        teams=RawFixtureTeams(home=RawFixtureTeamRef(id=33), away=RawFixtureTeamRef(id=34)),
        goals=RawFixtureScore(),
        score=RawFixtureScores(halftime=RawFixtureScore()),
    )

    result = map_fixture(raw)

    assert result.status == "SCHEDULED"


def test_map_fixture_event_parses_time_and_players():
    raw = RawFixtureEventEntry(
        time={"elapsed": 55, "extra": None},
        team=RawEventTeam(id=33),
        player=RawEventPlayer(id=500),
        assist=RawEventPlayer(id=501),
        type="Goal",
        detail="Normal Goal",
    )

    result = map_fixture_event(raw, match_source_id="1001")

    assert result.event_type == "GOAL"
    assert result.player_source_id == "500"
    assert result.related_player_source_id == "501"
    assert result.minute == 55
    assert result.extra_minute is None


def test_map_fixture_statistics_parses_percentage_strings_and_nulls():
    raw = RawFixtureStatisticsEntry(
        team=RawFixtureTeamRef(id=33),
        statistics=[
            RawStatisticValue(type="Ball Possession", value="55%"),
            RawStatisticValue(type="Total Shots", value=12),
            RawStatisticValue(type="Offsides", value=None),
        ],
    )

    result = map_fixture_statistics(raw, match_source_id="1001")
    stat_by_type = {s.stat_type: s.stat_value for s in result}

    assert stat_by_type["ball_possession"] == 55.0
    assert stat_by_type["total_shots"] == 12
    assert stat_by_type["offsides"] is None
