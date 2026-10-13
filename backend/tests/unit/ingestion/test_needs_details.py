from datetime import UTC, datetime, timedelta

from soccera.ingestion.sync.pipeline import needs_details
from soccera.storage.models.match import Match

KICKOFF = datetime(2026, 10, 11, 23, 0, tzinfo=UTC)


def _match(status: str, details_synced_at: datetime | None) -> Match:
    return Match(status=status, match_date=KICKOFF, details_synced_at=details_synced_at)


def test_finished_match_never_detail_synced_needs_details():
    assert needs_details(_match("FINISHED", None)) is True


def test_detail_fetched_mid_game_is_stale_once_finished():
    assert needs_details(_match("FINISHED", KICKOFF + timedelta(minutes=50))) is True


def test_detail_fetched_after_final_whistle_is_fresh():
    assert needs_details(_match("FINISHED", KICKOFF + timedelta(hours=3))) is False


def test_unfinished_matches_never_need_details():
    assert needs_details(_match("SCHEDULED", None)) is False
    assert needs_details(_match("LIVE", None)) is False
