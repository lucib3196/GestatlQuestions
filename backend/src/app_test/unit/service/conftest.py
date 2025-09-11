# Third-party
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from sqlmodel import Session, create_engine, SQLModel
from dataclasses import dataclass
from uuid import UUID, uuid4
from types import SimpleNamespace

# Local
from src.api.database.database import Base
from src.api.core import settings
from src.api.service import question_storage_service as qs
from pathlib import Path


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
def session():
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


@pytest.fixture
def patch_question_dir(monkeypatch):
    """Patch QUESTIONS_DIRNAME to point to a test directory."""
    dir_name = "test_question"
    monkeypatch.setattr(settings, "QUESTIONS_DIRNAME", f"{dir_name}")
    return dir_name


@pytest.fixture
def patch_questions_path(monkeypatch, tmp_path, patch_question_dir):
    """Patch BASE_PATH and QUESTIONS_PATH to use a temporary directory."""
    base_path = tmp_path.resolve()
    monkeypatch.setattr(settings, "BASE_PATH", str(base_path))

    questions_path = base_path / patch_question_dir
    monkeypatch.setattr(settings, "QUESTIONS_PATH", str(questions_path))

    return questions_path
