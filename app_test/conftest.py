# Third-party
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine, Session

from backend_api.main import get_application
from backend_api.data.database import Base, get_session
from backend_api.core.config import settings

# Local services
from backend_api.data import language_db as language_service
from backend_api.data import qtype_db as qtype_service
from backend_api.data import question_db as question_service
from backend_api.data import topic_db as topic_service
from backend_api.service import question_crud

from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def on_startup_test(app: FastAPI):
    # skip init_db in tests
    yield


@pytest.fixture(scope="session")
def engine():
    """Create a dedicated in-memory test engine."""
    settings.ENV = "testing"
    TEST_DB_URL = "sqlite:///:memory:"

    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(engine):
    """Provide a new SQLModel session for each test."""
    with Session(engine) as session:
        yield session
        session.rollback()  # rollback ensures isolation


@pytest.fixture(scope="function")
def test_client(db_session):
    """FastAPI TestClient with DB session override."""
    app = get_application()
    app.router.lifespan_context = on_startup_test

    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # db_session closed by fixture

    app.dependency_overrides[get_session] = override_get_db

    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def _clean_db(db_session):
    """Auto-clean database after each test."""
    yield
    question_service.delete_all_questions(db_session)
    topic_service.delete_all_topics(db_session)
    language_service.delete_all_languages(db_session)
    qtype_service.delete_all_qtypes(db_session)
    db_session.commit()
