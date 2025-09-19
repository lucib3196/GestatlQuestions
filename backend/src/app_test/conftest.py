# Configuration file for tests – these are global and generic

# --- Standard Library ---
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

# --- Third-Party ---
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings
from sqlmodel import Session, SQLModel, create_engine


# --- Internal ---
from src.api.core import settings, logger
from src.api.database.database import Base, get_session
from src.api.main import get_application


@asynccontextmanager
async def on_startup_test(app: FastAPI):
    # skip init_db in tests
    yield


## Setting up the database manually set to test, then
## Add a clean up function
@pytest.fixture(scope="function")
def test_engine(tmp_path):
    url = f"sqlite:///{tmp_path}/test.db"
    engine = create_engine(
        url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Provide a new SQLModel session for each test."""
    with Session(test_engine) as session:
        yield session
        session.rollback()  # rollback ensures isolation


@pytest.fixture(autouse=True)
def _clean_db(db_session, test_engine):
    logger.debug("Cleaning Database")
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)


@pytest.fixture(scope="function")
def test_client(db_session):
    app = get_application()

    app.router.lifespan_context = on_startup_test

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = override_get_db

    with TestClient(app) as client:
        yield client


# Dummy Session for Database
@dataclass
class FakeQuestion:
    id: UUID
    title: str | None
    local_path: str | None


class DummySession:
    def __init__(self):
        self.committed = False
        self.refreshed = False

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed = True

    def add(self, obj):
        pass


@pytest.fixture
def dummy_session():
    return DummySession()


def make_qc_stub(question: "FakeQuestion", session: DummySession):
    """Return a qc stub with async get_question_by_id."""

    async def _get_question_by_id(qid, _session):
        return question

    async def _safe_refresh_question(qid, _session):
        # Call DummySession methods, don't overwrite them
        _session.commit()
        _session.refresh(question)
        return question

    return SimpleNamespace(
        get_question_by_id=_get_question_by_id,
        safe_refresh_question=_safe_refresh_question,
    )


# Globa Fixtures
@pytest.fixture
def patch_question_dir(monkeypatch):
    """Patch QUESTIONS_DIRNAME to a test directory name."""
    dir_name = "test_question"
    monkeypatch.setattr(settings, "QUESTIONS_DIRNAME", dir_name)
    return dir_name


@pytest.fixture
def patch_questions_path(monkeypatch, tmp_path, patch_question_dir):
    """Patch BASE_PATH and QUESTIONS_PATH to a temporary directory on disk."""
    base_path = tmp_path.resolve()
    monkeypatch.setattr(settings, "BASE_PATH", str(base_path))

    questions_path = base_path / patch_question_dir
    questions_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(settings, "QUESTIONS_PATH", str(questions_path))

    return questions_path


class TestConfig(BaseSettings):
    asset_path: Path


test_config = TestConfig(asset_path=Path("./assets").resolve())


@pytest.fixture
def get_asset_path():
    return test_config.asset_path


# Testing logs
from src.api.core.logging import in_test_ctx

@pytest.fixture(autouse=True)
def mark_logs_in_test():
    token = in_test_ctx.set(True)
    yield
    in_test_ctx.reset(token)


if __name__ == "__main__":
    print(test_config)
