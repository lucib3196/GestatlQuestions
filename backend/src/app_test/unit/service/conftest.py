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


@pytest.fixture
def patch_questions_path(monkeypatch, tmp_path):
    """Point QUESTIONS_PATH at a temporary directory."""
    # Patch the settings object *inside* the module under test
    dummy_path = Path(str(tmp_path)) / "question_dummy"
    monkeypatch.setattr(settings, "QUESTIONS_PATH", str(dummy_path))
    return dummy_path


def make_qc_stub(question: FakeQuestion):
    """Return a qc stub with async get_question_by_id."""

    async def _get_question_by_id(qid, session):
        return question

    return SimpleNamespace(get_question_by_id=_get_question_by_id)
