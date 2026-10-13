from collections.abc import Generator

from sqlalchemy.orm import Session

from soccera.storage.database import session_scope


def get_db() -> Generator[Session, None, None]:
    with session_scope() as session:
        yield session
