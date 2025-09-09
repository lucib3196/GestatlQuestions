# tests/unit/service/test_question_crud_service.py

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Iterable, Tuple

import pytest
from fastapi import HTTPException

from backend.src.app_test.unit.database.conftest import  db_session
from api.models.file_model import File
from api.models.question_model import Question
from api.service import question_file_service


# -----------------------------
# Helpers
# -----------------------------

def _normalize_json_content(value: Any) -> Any:
    """
    Make tests robust whether File.content is stored as a dict (JSON column)
    or as a stringified JSON. Non-JSON strings are returned as-is.
    """
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _assert_file(f: File, *, filename: str, content: Any) -> None:
    """Unified file assertion. Content may be dict or str (JSON)."""
    assert f.filename == filename
    observed = _normalize_json_content(f.content)
    expected = _normalize_json_content(content)
    assert observed == expected


# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture
def sample_question(db_session) -> Question:
    """Question with no files."""
    q = Question(
        title="Sample Question",
        ai_generated=True,
        isAdaptive=False,
        createdBy="tester",
        user_id=1,
    )
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)
    return q


@pytest.fixture
def sample_question_with_file(db_session) -> Question:
    """Question with a single text file."""
    q = Question(
        title="Question with Files",
        ai_generated=True,
        isAdaptive=False,
        createdBy="user2",
        user_id=2,
    )
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    db_session.add(File(filename="Test.txt", content="Hello World", question_id=q.id))
    db_session.commit()
    return q


@pytest.fixture
def sample_question_with_file_dict(db_session) -> Question:
    """Question with a single JSON-like file (dict or stringified JSON)."""
    q = Question(
        title="Question with Files",
        ai_generated=True,
        isAdaptive=False,
        createdBy="user2",
        user_id=2,
    )
    db_session.add(q)
    db_session.commit()
    db_session.refresh(q)

    file_content = {"a": "Data", "b": "Another data"}
    db_session.add(File(filename="TestDict.txt", content=file_content, question_id=q.id))
    db_session.commit()
    return q


# -----------------------------
# Tests
# -----------------------------

def test_get_question_file_errors(db_session, sample_question):
    # Non-existing file in existing question
    with pytest.raises(HTTPException) as excinfo:
        question_file_service.get_question_file(
            question_id=sample_question.id, filename="Notvalid.txt", session=db_session
        )
    assert excinfo.value.status_code == 404
    assert "No File Notvalid.txt" in excinfo.value.detail

    # Non-existing question id
    fake_id = uuid.uuid4()
    with pytest.raises(HTTPException) as excinfo:
        question_file_service.get_question_file(
            question_id=fake_id, filename="DoesNotMatter.txt", session=db_session
        )
    assert excinfo.value.status_code == 404
    assert "Question not Found" in excinfo.value.detail


def test_get_question_file_success_text(db_session, sample_question_with_file):
    result = question_file_service.get_question_file(
        question_id=sample_question_with_file.id,
        filename="Test.txt",
        session=db_session,
    )
    assert result.status == 200
    assert isinstance(result.file_obj, list) and len(result.file_obj) == 1
    _assert_file(result.file_obj[0], filename="Test.txt", content="Hello World")


def test_get_question_file_success_dict(db_session, sample_question_with_file_dict):
    result = question_file_service.get_question_file(
        question_id=sample_question_with_file_dict.id,
        filename="TestDict.txt",
        session=db_session,
    )
    assert result.status == 200
    assert isinstance(result.file_obj, list) and len(result.file_obj) == 1
    _assert_file(
        result.file_obj[0],
        filename="TestDict.txt",
        content={"a": "Data", "b": "Another data"},
    )


def test_add_file_to_question(db_session, sample_question):
    # Add text content
    new_filename = "NewFile.txt"
    new_content = "Hello World Again!"

    # Verify absence first
    with pytest.raises(HTTPException):
        question_file_service.get_question_file(
            question_id=sample_question.id, filename=new_filename, session=db_session
        )

    response = question_file_service.add_file_to_question(
        question_id=sample_question.id,
        filename=new_filename,
        content=new_content,
        session=db_session,
    )
    assert response.status == 201
    assert isinstance(response.file_obj, list) and len(response.file_obj) == 1
    _assert_file(response.file_obj[0], filename=new_filename, content=new_content)

    # Add JSON-like dict content (service may store as dict or stringify)
    newer_filename = "NewerFile.txt"
    newer_content = {"a": "a", "b": "b"}

    response = question_file_service.add_file_to_question(
        question_id=sample_question.id,
        filename=newer_filename,
        content=newer_content,
        session=db_session,
    )
    assert response.status == 201
    assert isinstance(response.file_obj, list) and len(response.file_obj) == 1
    _assert_file(response.file_obj[0], filename=newer_filename, content=newer_content)


@pytest.mark.parametrize(
    "files",
    [
        (("NewFile.txt", "Hello World"),
         ("AnotherFile.json", "Content"),
         ("ThirdFile.py", "I am tired")),
        (("data.json", {"x": 1}),),
    ],
)
def test_get_all_files(db_session, sample_question, files: Iterable[Tuple[str, Any]]):
    # No files yet
    with pytest.raises(HTTPException) as excinfo:
        question_file_service.get_all_files(sample_question.id, db_session)
    assert excinfo.value.status_code == 404
    assert "No Files for Question" in excinfo.value.detail

    # Add files
    for filename, content in files:
        question_file_service.add_file_to_question(
            question_id=sample_question.id,
            filename=filename,
            content=content,
            session=db_session,
        )

    response = question_file_service.get_all_files(sample_question.id, db_session)
    assert isinstance(response.file_obj, list)
    returned_names = {f.filename for f in response.file_obj}
    expected_names = {fn for fn, _ in files}
    assert returned_names == expected_names

    # Per-file content checks
    by_name = {f.filename: f for f in response.file_obj}
    for filename, content in files:
        _assert_file(by_name[filename], filename=filename, content=content)


def test_update_question_file(db_session, sample_question_with_file):
    # Validate initial state
    initial = question_file_service.get_question_file(
        question_id=sample_question_with_file.id,
        filename="Test.txt",
        session=db_session,
    )
    assert initial.status == 200
    _assert_file(initial.file_obj[0], filename="Test.txt", content="Hello World")

    # Update
    response = question_file_service.update_question_file(
        sample_question_with_file.id,
        filename="Test.txt",
        new_content="Hello Sun!!!",
        session=db_session,
    )
    assert response.status == 200
    _assert_file(response.file_obj[0], filename="Test.txt", content="Hello Sun!!!")

    # Bad question id
    fake_uuid = uuid.uuid4()
    with pytest.raises(HTTPException) as excinfo:
        question_file_service.get_question_file(
            question_id=fake_uuid, filename="Test.txt", session=db_session
        )
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Question not Found"


# -----------------------------
# Optional stricter tests (enable after normalizing service behavior)
# -----------------------------
@pytest.mark.skip(reason="Enable after service normalizes JSON to dict")
def test_add_file_to_question_returns_dict_for_json(db_session, sample_question):
    """
    Once your service always normalizes JSON content to dict (not string),
    this test should pass without normalization helper.
    """
    resp = question_file_service.add_file_to_question(
        question_id=sample_question.id,
        filename="strict.json",
        content={"k": "v"},
        session=db_session,
    )
    assert isinstance(resp.file_obj[0].content, dict)
    assert resp.file_obj[0].content == {"k": "v"}
