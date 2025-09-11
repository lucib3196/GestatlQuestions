import json
import uuid
from typing import Any, Dict, Iterable, Tuple

import pytest
import pytest_asyncio
from fastapi import HTTPException

from src.app_test.integration.fixtures.fixture_question_storage import *
from src.api.models.question_model import Question
from src.api.service import question_storage_service as qs


@pytest.mark.asyncio
async def test_get_question_file_success_text(db_session, sample_question_with_file):
    result = await qs.get_file_content(
        question_id=sample_question_with_file.id,
        filename="Test.txt",
        session=db_session,
    )

    assert result.status == 200
    assert isinstance(result.files, list) and len(result.files) == 1

    assert result.files[0].filename == "Test.txt"  # type: ignore
    assert result.files[0].content == "Hello World"  # type: ignore


@pytest.mark.asyncio
async def test_get_question_file_success_dict(
    db_session, sample_question_with_file_dict
):
    result = await qs.get_file_content(
        question_id=sample_question_with_file_dict.id,
        filename="Dummy.json",
        session=db_session,
    )
    assert result.status == 200
    assert isinstance(result.files, list) and len(result.files) == 1

    assert result.files[0].filename == "Dummy.json"  # type: ignore
    assert json.loads(result.files[0].content) == {"a": "Data", "b": "Another data"}  # type: ignore


@pytest.mark.asyncio
async def test_get_question_file_errors(db_session, sample_question):
    # Non-existing file in existing question
    with pytest.raises(HTTPException) as excinfo:
        await qs.get_file_content(
            question_id=sample_question.id, filename="Notvalid.txt", session=db_session
        )

    assert excinfo.value.status_code == 400
    assert "No Question Path Set for Sample Question" in excinfo.value.detail

    # Non-existing question id
    fake_id = uuid.uuid4()
    with pytest.raises(HTTPException) as excinfo:
        await qs.get_file_content(
            question_id=fake_id, filename="DoesNotMatter.txt", session=db_session
        )
    assert excinfo.value.status_code == 404
    assert "Question does not exist" in excinfo.value.detail


@pytest.mark.asyncio
async def test_add_file_to_question(db_session, sample_question):
    # Add text content
    new_filename = "NewFile.txt"
    new_content = "Hello World Again!"

    # Verify absence first
    with pytest.raises(HTTPException):
        await qs.get_file_content(
            question_id=sample_question.id, filename=new_filename, session=db_session
        )

    response = await qs.write_file_to_directory(
        question_id=sample_question.id,
        file_data=qs.FileData(filename=new_filename, content=new_content),
        session=db_session,
    )
    assert response.status == 200

    retrieved = await qs.get_file_content(
        question_id=sample_question.id, filename=new_filename, session=db_session
    )
    assert retrieved.files[0].filename == new_filename  # type: ignore
    assert retrieved.files[0].content == new_content  # type: ignore


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "files",
    [
        (
            ("NewFile.txt", "Hello World"),
            ("AnotherFile.json", "Content"),
            ("ThirdFile.py", "I am tired"),
        ),
        (("data.json", {"x": 1}),),
    ],
)
async def test_get_all_files(
    db_session, sample_question, files: Iterable[Tuple[str, Any]]
):
    # No files yet
    with pytest.raises(HTTPException) as excinfo:
        await qs.get_files_from_directory(sample_question.id, db_session)
    assert excinfo.value.status_code == 400
    assert "No Question Path Set for Sample Question" in excinfo.value.detail

    # Add files
    for filename, content in files:
        await qs.write_file_to_directory(
            question_id=sample_question.id,
            file_data=qs.FileData(filename=filename, content=content),
            session=db_session,
        )

    response = await qs.get_files_from_directory(sample_question.id, db_session)
    assert isinstance(response.files, list)
    # returned_names = {f.filename for f in response.files}  # type: ignore
    # expected_names = {fn for fn, _ in files}
    # assert returned_names == expected_names

    # # Per-file content checks
    # by_name = {f.filename: f for f in response.files}  # type: ignore
    # for filename, content in files:
    #     _assert_file(by_name[filename], filename=filename, content=content)  # type: ignore


@pytest.mark.asyncio
async def test_update_question_file(db_session, sample_question_with_file):
    # Validate initial state
    initial = await qs.get_file_content(
        question_id=sample_question_with_file.id,
        filename="Test.txt",
        session=db_session,
    )
    assert initial.status == 200
    _assert_file(initial.files[0], filename="Test.txt", content="Hello World")  # type: ignore

    # Update
    response = await qs.update_file_content(
        sample_question_with_file.id,
        filename="Test.txt",
        new_content="Hello Sun!!!",
        session=db_session,
    )
    assert response.status == 200
    _assert_file(response.files[0], filename="Test.txt", content="Hello Sun!!!")  # type: ignore

    # Bad question id
    fake_uuid = uuid.uuid4()
    with pytest.raises(HTTPException) as excinfo:
        await qs.get_file_content(
            question_id=fake_uuid, filename="Test.txt", session=db_session
        )
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Question does not exist"


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


def _assert_file(f: File | FileData, *, filename: str, content: Any) -> None:
    """Unified file assertion. Content may be dict or str (JSON)."""
    assert f.filename == filename
    observed = _normalize_json_content(f.content)
    expected = _normalize_json_content(content)
    assert observed == expected
