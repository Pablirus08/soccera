import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from soccera.storage.models import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://soccera:soccera@localhost:5432/soccera_test"
)


@pytest.fixture(scope="session")
def engine():
    try:
        eng = create_engine(TEST_DATABASE_URL)
        with eng.connect():
            pass
    except Exception as exc:
        pytest.skip(f"Test database not reachable at {TEST_DATABASE_URL}: {exc}")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def session(engine) -> Session:
    session_factory = sessionmaker(bind=engine)
    db_session = session_factory()
    yield db_session
    db_session.rollback()
    db_session.close()
