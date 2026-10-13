from typing import Any, ClassVar, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from soccera.storage.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class SourceKeyedRepository(Generic[ModelT]):
    """
    Base for repositories on entities that carry SourceMixin (source, source_id).
    upsert() is what makes re-running a sync job idempotent: the same
    provider record always resolves to the same row.
    """

    model: ClassVar[type[Base]]

    def __init__(self, session: Session):
        self.session = session

    def get_by_source(self, source: str, source_id: str) -> ModelT | None:
        stmt = select(self.model).where(
            self.model.source == source, self.model.source_id == source_id
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_id(self, entity_id: int) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def upsert(self, source: str, source_id: str, **fields: Any) -> ModelT:
        instance = self.get_by_source(source, source_id)
        if instance is None:
            instance = self.model(source=source, source_id=source_id, **fields)
            self.session.add(instance)
        else:
            for key, value in fields.items():
                setattr(instance, key, value)
        self.session.flush()
        return instance
