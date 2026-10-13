from datetime import datetime, timezone

from soccera.storage.repositories import LeagueRepository, MatchRepository, SeasonRepository, TeamRepository


def test_league_upsert_is_idempotent_on_source_id(session):
    repo = LeagueRepository(session)

    first = repo.upsert(
        source="api_football", source_id="39", name="Premier League", country="England", type="league"
    )
    second = repo.upsert(
        source="api_football",
        source_id="39",
        name="Premier League (renamed)",
        country="England",
        type="league",
    )

    assert first.id == second.id
    assert second.name == "Premier League (renamed)"


def test_match_upsert_and_date_range_lookup(session):
    league = LeagueRepository(session).upsert(
        source="api_football", source_id="39", name="Premier League"
    )
    season = SeasonRepository(session).upsert(league_id=league.id, year=2024)
    team_repo = TeamRepository(session)
    home = team_repo.upsert(source="api_football", source_id="33", name="Man United")
    away = team_repo.upsert(source="api_football", source_id="34", name="Newcastle")

    match_repo = MatchRepository(session)
    match_repo.upsert(
        source="api_football",
        source_id="1001",
        league_id=league.id,
        season_id=season.id,
        home_team_id=home.id,
        away_team_id=away.id,
        match_date=datetime(2024, 8, 20, tzinfo=timezone.utc),
        status="SCHEDULED",
    )

    matches = match_repo.get_by_date_range(
        datetime(2024, 8, 1, tzinfo=timezone.utc), datetime(2024, 9, 1, tzinfo=timezone.utc)
    )

    assert len(matches) == 1
    assert matches[0].source_id == "1001"


def test_match_upsert_updates_status_and_score_on_second_call(session):
    league = LeagueRepository(session).upsert(
        source="api_football", source_id="39", name="Premier League"
    )
    season = SeasonRepository(session).upsert(league_id=league.id, year=2024)
    team_repo = TeamRepository(session)
    home = team_repo.upsert(source="api_football", source_id="33", name="Man United")
    away = team_repo.upsert(source="api_football", source_id="34", name="Newcastle")
    match_repo = MatchRepository(session)

    match_repo.upsert(
        source="api_football",
        source_id="1001",
        league_id=league.id,
        season_id=season.id,
        home_team_id=home.id,
        away_team_id=away.id,
        match_date=datetime(2024, 8, 20, tzinfo=timezone.utc),
        status="SCHEDULED",
    )
    updated = match_repo.upsert(
        source="api_football",
        source_id="1001",
        league_id=league.id,
        season_id=season.id,
        home_team_id=home.id,
        away_team_id=away.id,
        match_date=datetime(2024, 8, 20, tzinfo=timezone.utc),
        status="LIVE",
        home_score=1,
        away_score=0,
    )

    assert updated.status == "LIVE"
    assert updated.home_score == 1
    live_matches = match_repo.get_live()
    assert len(live_matches) == 1
