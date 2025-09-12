# --- Third-Party ---
import pytest
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

# --- Internal ---
from src.api.core import settings
from src.api.database.database import Base, get_session, SessionDep
from src.api.main import get_application
from src.api import models  # ensures tables are registered


# ---------------------------------------------------------------------------
# Lifespan override
# ---------------------------------------------------------------------------


@asynccontextmanager
async def on_startup_test(app: FastAPI):
    """Skip init_db during tests."""
    yield


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------


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
    """Provide a fresh SQLModel session for each test."""
    with Session(test_engine) as session:
        yield session


# ---------------------------------------------------------------------------
# FastAPI test client fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def test_client(db_session):
    app = get_application()

    app.router.lifespan_context = on_startup_test

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = override_get_db

    with TestClient(app) as client:
        yield client


# ---------------------------------------------------------------------------
# Path patching fixtures
# ---------------------------------------------------------------------------


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
