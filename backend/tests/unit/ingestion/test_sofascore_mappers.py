from soccera.ingestion.providers.costa_rica.mappers import map_lineup_player, map_player
from soccera.ingestion.providers.costa_rica.schemas import (
    RawCountry,
    RawLineupPlayer,
    RawSquadPlayer,
)


def _raw_player(**overrides) -> RawSquadPlayer:
    fields = {
        "id": 971301,
        "name": "Guido Jiménez",
        "firstName": "",
        "lastName": "",
        "position": "G",
        "dateOfBirthTimestamp": 834451200,
        "country": RawCountry(name="Costa Rica"),
    }
    return RawSquadPlayer(**{**fields, **overrides})


def test_map_player_normalizes_position_and_empty_names():
    result = map_player(_raw_player())

    assert result.source_id == "971301"
    assert result.position == "Goalkeeper"
    assert result.nationality == "Costa Rica"
    assert result.first_name is None  # Sofascore sends "" for unknown names
    assert result.birth_date is not None


def test_map_lineup_player_splits_core_fields_from_stats():
    raw = RawLineupPlayer(
        player=_raw_player(),
        teamId=531301,
        shirtNumber=99,
        position="G",
        substitute=False,
        statistics={
            "minutesPlayed": 90,
            "rating": 6.7,
            "saves": 3,
            "expectedGoals": 0.0,
            "ratingVersions": {"original": 6.7, "alternative": 6.9},
            "statisticsType": {"sportSlug": "football"},
        },
    )

    result = map_lineup_player(raw, match_source_id="16317836", team_source_id="531301")

    assert result.is_starter is True
    assert result.minutes_played == 90
    assert result.rating == 6.7
    assert result.position == "Goalkeeper"
    # minutesPlayed/rating are promoted out of stats; nested objects are dropped.
    assert result.stats == {"saves": 3.0, "expectedGoals": 0.0}


def test_map_lineup_player_unused_substitute_has_no_minutes():
    raw = RawLineupPlayer(player=_raw_player(position="F"), substitute=True)

    result = map_lineup_player(raw, match_source_id="1", team_source_id="2")

    assert result.is_starter is False
    assert result.minutes_played is None
    assert result.rating is None
    assert result.stats == {}
