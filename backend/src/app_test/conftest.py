# Configuration file for tests – these are global and generic

# --- Standard Library ---
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

# Testing logs
from src.api.core.logging import in_test_ctx

# --- Third-Party ---
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings
from sqlmodel import Session, SQLModel, create_engine
from pydantic import BaseModel
from typing import List

# --- Internal ---
from src.api.core import settings, logger
from src.api.database.database import Base, get_session
from src.api.main import get_application
from src.api.service.storage import StorageService
from src.api.response_models import FileData
from src.api.service.storage.cloud_storage import FireCloudStorageService
from src.api.service.storage.local_storage import LocalStorageService
from src.api.service.question_manager import QuestionManager
from src.api.dependencies import get_question_manager
from src.api.models import Question


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


@pytest.fixture(scope="function", params=["local", "cloud"])
def test_client(db_session, request, question_manager_cloud, question_manager_local):
    app = get_application()

    storage_type = request.param
    if storage_type == "cloud":
        qm = question_manager_cloud
    elif storage_type == "local":
        qm = question_manager_local
    else:
        raise ValueError("Incorrect storage type")

    app.router.lifespan_context = on_startup_test

    def override_get_db():
        yield db_session

    async def override_get_qm():
        yield qm

    app.dependency_overrides[get_session] = override_get_db
    app.dependency_overrides[get_question_manager] = override_get_qm

    with TestClient(app) as client:
        yield client


class FakeQuestion(BaseModel):
    """A fake Question model for testing."""

    title: str | None
    local_path: str | None
    blob_name: str | None = None
    id: UUID


class DummySession:
    """A fake DB session used for testing."""

    def __init__(self):
        self.committed = False
        self.refreshed = False

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        self.refreshed = True

    def add(self, obj):
        pass


class DummyStorage(StorageService):
    """A fake storage service used for testing."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.basename = self.path.name

    def get_basename(self) -> str | Path:
        return self.basename

    def does_directory_exist(self, identifier: str) -> bool:
        return self.get_directory(identifier).exists()

    def create_directory(self, identifier: str) -> Path:
        Path.mkdir(self.get_directory(identifier), parents=True, exist_ok=True)
        return self.get_directory(identifier)

    def get_directory(self, identifier: str) -> Path:
        return self.path / identifier

    def get_filepath(self, identifier: str, filename: str) -> Path:
        return super().get_filepath(identifier, filename)

    def save_file(
        self,
        identifier: str,
        filename: str,
        content: str | dict | list | bytes | bytearray,
        overwrite: bool = True,
    ) -> Path:
        return super().save_file(identifier, filename, content, overwrite)

    def get_files_names(self, identifier: str) -> list[str]:
        return super().get_files_names(identifier)

    def get_file(self, identifier: str, filename: str) -> bytes | None:
        return super().get_file(identifier, filename)

    def delete_file(self, identifier: str, filename: str) -> None:
        return super().delete_file(identifier, filename)


def make_qc_stub(question: FakeQuestion, session: DummySession):
    """Return a qc stub with async get_question_by_id and safe_refresh_question."""

    async def _get_question_by_id(qid, _session):
        return question

    async def _safe_refresh_question(qid, _session):
        _session.commit()
        _session.refresh(question)
        return question

    return SimpleNamespace(
        get_question_by_id=_get_question_by_id,
        safe_refresh_question=_safe_refresh_question,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def dummy_session():
    return DummySession()


@pytest.fixture
def dummy_storage(tmp_path):
    path = Path(tmp_path) / "questions"
    return DummyStorage(path)


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


@pytest.fixture(autouse=True)
def mark_logs_in_test():
    """Mark logs as being inside test context for duration of each test."""
    token = in_test_ctx.set(True)
    yield
    in_test_ctx.reset(token)



from src.app_test.fixtures.fixture_crud import *



@pytest.fixture
def qpayload_bad():
    return {"Data": "Some Content"}


@pytest.fixture
def file_data_payload() -> List[FileData]:
    """Provide a list of FileData objects with string, dict, and binary content."""
    text_content = "Hello World"
    dict_content = {"key": "value", "number": 123}
    binary_content = b"\x00\x01\x02\x03"

    return [
        FileData(filename="Test.txt", content=text_content),
        FileData(filename="Config.json", content=dict_content),
        FileData(filename="Binary.bin", content=binary_content),
    ]


@pytest.fixture
def question_file_payload() -> List[FileData]:
    files_data = [
        ("question.html", "Some question text"),
        ("solution.html", "Some solution"),
        ("server.js", "some code content"),
        ("meta.json", {"content": "some content"}),
    ]
    return [FileData(filename=f[0], content=f[1]) for f in files_data]


@pytest.fixture
def question_additional_metadata():
    return {
        "topics": ["Mechanics", "Statics"],
        "languages": ["python", "javascript"],
        "qtype": ["numeric"],
    }


# Storage Fixtures
@pytest.fixture(scope="function")
def cloud_storage_service():
    """
    Provides a FireCloudStorageService connected to the configured test bucket.
    """
    cred_path = settings.FIREBASE_PATH
    bucket_name = settings.STORAGE_BUCKET
    base_name = "integration_test"

    assert cred_path, "FIREBASE_PATH must be set in settings"
    assert bucket_name, "STORAGE_BUCKET must be set in settings"

    return FireCloudStorageService(
        cred_path=cred_path, bucket_name=bucket_name, base_name=base_name
    )


@pytest.fixture(autouse=True)
def clean_up_cloud(cloud_storage_service):
    # Setup code (before test runs)
    yield
    # Teardown code (after test finishes)
    cloud_storage_service.hard_delete()
    logger.debug("Deleting Bucket Cleaning Up")


@pytest.fixture
def local_storage(tmp_path):
    """Provide a LocalStorageService rooted in a temp directory."""
    base = tmp_path / "questions"
    return LocalStorageService(base)


@pytest.fixture
def question_manager_local(local_storage):
    """Provide a QuestionManager using LocalStorageService."""
    return QuestionManager(local_storage, "local")


@pytest.fixture
def question_manager_cloud(cloud_storage_service):
    return QuestionManager(cloud_storage_service, "cloud")

@pytest.fixture(scope="function", params=["local", "cloud"])
def question_manager(request,question_manager_local, question_manager_cloud):
    storage_type = request.param
    if storage_type == "cloud":
        qm = question_manager_cloud
    elif storage_type == "local":
        qm = question_manager_local
    else:
        raise ValueError("Incorrect storage type")
    return qm

# ---------------------------------------------------------------------------
# Debug Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(test_config)
