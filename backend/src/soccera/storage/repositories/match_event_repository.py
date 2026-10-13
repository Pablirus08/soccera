from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.storage.models.match_event import MatchEvent


class MatchEventRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_match(self, match_id: int) -> list[MatchEvent]:
        stmt = select(MatchEvent).where(MatchEvent.match_id == match_id).order_by(MatchEvent.minute)
        return list(self.session.execute(stmt).scalars())

    def replace_for_match(self, match_id: int, events: list[MatchEvent]) -> None:
        """
        Live event feeds are typically re-fetched as a full list per poll
        rather than diffed, so the simplest idempotent write is delete+insert.
        """
        stmt = select(MatchEvent).where(MatchEvent.match_id == match_id)
        for existing in self.session.execute(stmt).scalars():
            self.session.delete(existing)
        self.session.flush()
        self.session.add_all(events)
        self.session.flush()
