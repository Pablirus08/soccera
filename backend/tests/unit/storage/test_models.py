from sqlalchemy.orm import configure_mappers

from soccera.storage.models import Base


def test_all_model_relationships_configure_without_error():
    """
    Catches typos in string-based relationship() targets (e.g. Mapped["Seson"])
    that would otherwise only surface the first time the ORM is used.
    """
    configure_mappers()
    expected_tables = {
        "leagues",
        "seasons",
        "venues",
        "teams",
        "players",
        "team_players",
        "matches",
        "match_statistics",
        "match_events",
        "predictions",
        "ingestion_runs",
    }
    assert expected_tables.issubset(Base.metadata.tables.keys())
