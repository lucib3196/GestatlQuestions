import pytest
from pathlib import Path
from src.api.service import question_storage_service as qs
from starlette import status
import json
from typing import List
from fastapi import HTTPException
from src.utils import safe_dir_name
from src.app_test.conftest import *
from uuid import uuid4


@pytest.mark.asyncio
async def test_get_directory_when_local_path_already_set(
    monkeypatch, patch_questions_path, patch_question_dir, dummy_session
):
    """Return existing directory if local_path is already set; no DB commit/refresh should occur."""
    # Arrange
    question_title = "MyQuestion"
    safe_name = qs.safe_dir_name(question_title)

    rel_path = Path(patch_question_dir) / safe_name
    abs_path = Path(patch_questions_path) / safe_name
    abs_path.mkdir(parents=True)

    q = FakeQuestion(
        id=uuid4(), title=question_title, local_path=str(rel_path), blob_name=None
    )
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    # Act
    resp = await qs.get_question_directory(dummy_session, q.id)

    # Assert: response details
    assert resp.status == status.HTTP_200_OK
    assert "local path already set" in resp.detail.lower()

    # Assert: path handling
    assert abs_path.exists()
    assert resp.filepaths and isinstance(resp.filepaths, list)
    assert resp.filepaths[0] == str(rel_path)

    # Assert: session untouched
    assert not dummy_session.commit()
    assert not dummy_session.refresh(q)


@pytest.mark.asyncio
async def test_get_directory_when_local_path_missing(
    monkeypatch, patch_questions_path, patch_question_dir, dummy_session
):
    """Raise 400 if no local_path is set on the question."""
    # Arrange
    q = FakeQuestion(id=uuid4(), title="My Question", local_path=None)
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await qs.get_question_directory(dummy_session, q.id)

    assert excinfo.value.status_code == 400
    assert "no question path set" in excinfo.value.detail.lower()


@pytest.mark.asyncio
async def test_get_directory_when_path_set_but_dir_missing(
    monkeypatch, patch_question_dir, dummy_session
):
    """Raise 400 if local_path is set but the directory does not exist on disk."""
    # Arrange
    question_title = "MyQuestionNoDir"
    safe_name = qs.safe_dir_name(question_title)
    rel_path = Path(patch_question_dir) / safe_name

    q = FakeQuestion(id=uuid4(), title=question_title, local_path=str(rel_path))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await qs.get_question_directory(dummy_session, q.id)

    assert excinfo.value.status_code == 400
    # assert "directory may not exist" in excinfo.value.detail.lower()


@pytest.mark.asyncio
async def test_set_or_get_directory_returns_existing_path_without_changes(
    monkeypatch, patch_questions_path, dummy_session
):
    question_title = "MyExistingQuestion"
    # Arrange: question already has a valid local_path
    existing = patch_questions_path / question_title
    existing.mkdir(parents=True)
    q = FakeQuestion(id=uuid4(), title=question_title, local_path=str(existing))
    # stub qc in the module under test
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))
    # Act
    resp = await qs.set_or_get_directory(q.id, dummy_session)

    # Assert that response was successful and right type
    assert resp.status == status.HTTP_200_OK
    assert "local path already set" in resp.detail.lower()

    # Assert the filepath exist and created
    assert len(resp.filepaths) == 1

    retrieved_path = patch_questions_path / resp.filepaths[0]
    assert retrieved_path.resolve() == existing

    # Check database there should be no changes at this point
    assert dummy_session.committed is False
    assert dummy_session.refreshed is False


@pytest.mark.asyncio
async def test_set_or_get_directory_creates_new_directory_when_not_set(
    monkeypatch, patch_questions_path, dummy_session
):
    question_title = "My New Question"
    q = FakeQuestion(id=uuid4(), title=question_title, local_path=None)
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    resp = await qs.set_or_get_directory(dummy_session, q.id)

    # Assert that response was successful and right type
    assert resp.status == status.HTTP_201_CREATED
    assert "created successfully" in resp.detail.lower()
    assert isinstance(resp.filepaths, list)
    assert len(resp.filepaths) == 1

    # Check the filepath
    created_path = resp.filepaths[0]
    assert created_path  # string
    assert (patch_questions_path / qs.safe_dir_name(str(q.title))).exists()

    # Assert database changes
    assert dummy_session.committed is True
    assert dummy_session.refreshed is True
    # also check Question was updated
    assert q.local_path == created_path


@pytest.mark.asyncio
async def test_set_or_get_directory_appends_id_on_name_collision(
    monkeypatch, patch_questions_path, patch_question_dir, dummy_session
):
    """If a directory with the same name exists, append the UUID to avoid collision."""
    fixed_uuid = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    title = "Duplicate"

    # Create the base directory that will cause a collision
    base = patch_questions_path / qs.safe_dir_name(title)
    base.mkdir(parents=True)

    q = FakeQuestion(id=fixed_uuid, title=title, local_path=None)
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    # Act
    resp = await qs.set_or_get_directory(dummy_session, q.id)

    # Assert response
    assert resp.status == status.HTTP_201_CREATED

    # Build expected paths
    safe_dirname = qs.safe_dir_name(f"{title}_{fixed_uuid}")
    relative_path = Path(patch_question_dir) / safe_dirname
    expected_path = patch_questions_path / safe_dirname

    # Assert paths
    assert Path(resp.filepaths[0]) == Path(relative_path)
    assert expected_path.exists()


@pytest.mark.asyncio
async def test_write_files_returns_expected_response(
    monkeypatch, patch_questions_path, patch_question_dir, dummy_session
):
    """Ensure write_files_to_directory returns the correct response object with filedata and filepaths."""
    question_title = "QuestionWriteFiles"
    q = FakeQuestion(id=uuid4(), title=question_title, local_path=None)
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))
    await qs.set_or_get_directory(dummy_session, q.id)

    files_data = [
        qs.FileData(filename="readme.txt", content="hello"),
        qs.FileData(filename="config.json", content={"env": "dev", "debug": True}),
    ]

    # Act
    resp = await qs.write_files_to_directory(
        q.id, files_data=files_data, session=dummy_session
    )

    # Assert response structure
    assert resp.status == 200
    assert resp.filedata
    assert resp.filedata == files_data
    assert len(resp.filedata) == len(resp.filepaths)


@pytest.mark.asyncio
async def test_write_files_creates_files_on_disk(
    monkeypatch, patch_questions_path, patch_question_dir, dummy_session
):
    """Ensure write_files_to_directory actually writes files with correct contents to disk."""
    question_title = "QuestionWriteFiles"
    q = FakeQuestion(id=uuid4(), title=question_title, local_path=None)
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))
    await qs.set_or_get_directory(dummy_session, q.id)

    files_data = [
        qs.FileData(filename="readme.txt", content="hello"),
        qs.FileData(filename="config.json", content={"env": "dev", "debug": True}),
    ]

    # Act
    resp = await qs.write_files_to_directory(
        q.id, files_data=files_data, session=dummy_session
    )

    # Assert filesystem state
    for filedata, filepath in zip(resp.filedata, resp.filepaths):
        expected_rel = (
            Path(patch_question_dir)
            / qs.safe_dir_name(question_title)
            / filedata.filename
        )
        assert filepath == str(expected_rel), f"{filepath} mismatch"

        abs_path = (
            Path(patch_questions_path)
            / qs.safe_dir_name(question_title)
            / filedata.filename
        )
        assert abs_path.exists()

        if isinstance(filedata.content, dict):
            assert json.loads(abs_path.read_text(encoding="utf-8")) == filedata.content
        else:
            assert abs_path.read_text(encoding="utf-8") == filedata.content


@pytest.mark.asyncio
async def test_get_files_check_filedata(
    monkeypatch, patch_questions_path, dummy_session
):
    """Ensure get_files_from_directory returns written files."""
    question_title = "QuestionWriteFiles"
    q = FakeQuestion(id=uuid4(), title=question_title, local_path=None)
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))
    await qs.set_or_get_directory(dummy_session, q.id)
    files_data = [
        qs.FileData(filename="readme.txt", content="hello"),
        qs.FileData(filename="config.json", content={"env": "dev", "debug": True}),
    ]
    await qs.write_files_to_directory(
        q.id, files_data=files_data, session=dummy_session
    )
    # Act
    response = await qs.get_files_from_directory(q.id, session=dummy_session)
    # Assert
    assert len(response.filedata) == len(files_data)


@pytest.mark.asyncio
async def test_get_filename(monkeypatch, patch_questions_path, dummy_session):
    """Ensure get_file_path returns correct file contents."""
    existing = patch_questions_path / "already-there"
    existing.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    files_data = [
        qs.FileData(filename="readme.txt", content="hello"),
        qs.FileData(filename="config.json", content={"env": "dev", "debug": True}),
    ]
    await qs.write_files_to_directory(
        q.id, files_data=files_data, session=dummy_session
    )

    for f in files_data:
        r = await qs.get_file_path_abs(q.id, filename=f.filename, session=dummy_session)
        content = Path(r.filepaths[0]).read_text()

        if isinstance(f.content, dict):
            assert json.loads(content) == f.content
        else:
            assert content == f.content


@pytest.mark.asyncio
async def test_get_filename_empty(monkeypatch, patch_questions_path, dummy_session):
    """Ensure get_file_path raises if filename does not exist."""
    existing = patch_questions_path / "already-there"
    existing.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    with pytest.raises(HTTPException) as excinfo:
        await qs.get_file_path_abs(q.id, filename="NotExist.txt", session=dummy_session)

    assert excinfo.value.status_code == 400


@pytest.mark.asyncio
async def test_update_file(monkeypatch, patch_questions_path, dummy_session):
    """Ensure update_file_content overwrites files correctly."""
    existing = patch_questions_path / "already-there"
    existing.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    files_data = [
        qs.FileData(filename="readme.txt", content="hello"),
        qs.FileData(filename="config.json", content={"env": "dev", "debug": True}),
    ]
    await qs.write_files_to_directory(
        q.id, files_data=files_data, session=dummy_session
    )

    for f in files_data:
        new_content = "New Content"
        r = await qs.update_file_content(
            q.id, f.filename, new_content=new_content, session=dummy_session
        )
        c = Path(str(r.filepaths[0])).read_text()
        assert c == new_content


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fname,new_content,expect_reader",
    [
        ("readme.txt", "New Content", lambda p: Path(p).read_text()),
        (
            "config.json",
            {"env": "prod", "debug": False},
            lambda p: json.loads(Path(p).read_text()),
        ),
        ("binary.bin", b"\x00\x01\x02\x03", lambda p: Path(p).read_bytes()),
        ("notes with spaces.md", " spaced ok ", lambda p: Path(p).read_text()),
    ],
)
async def test_update_file_happy_paths(
    monkeypatch, patch_questions_path, dummy_session, fname, new_content, expect_reader
):
    """Ensure update_file_content overwrites str, dict->JSON, and bytes; respects safe filename normalization."""
    existing_dir = patch_questions_path / "already-there"
    existing_dir.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing_dir))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    # Prime directory with initial version
    initial = "hello" if not isinstance(new_content, (bytes, bytearray)) else b"hello"
    target = existing_dir / qs.safe_dir_name(fname)
    if isinstance(initial, str):
        target.write_text(initial)
    else:
        target.write_bytes(initial)

    resp = await qs.update_file_content(
        q.id, fname, new_content=new_content, session=dummy_session
    )

    # Assert content persisted
    persisted = expect_reader(resp.filepaths[0])
    if isinstance(new_content, dict):
        assert persisted == new_content
    else:
        assert persisted == new_content

    # Sanity check target file exists
    assert target.exists()
    assert Path(resp.filepaths[0]).resolve() == target.resolve()


@pytest.mark.asyncio
async def test_update_file_nonexistent_raises(
    monkeypatch, patch_questions_path, dummy_session
):
    """Updating a missing file should raise HTTPException."""
    base = patch_questions_path / "empty-dir"
    base.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="Ghost Q", local_path=str(base))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q, dummy_session))

    with pytest.raises(HTTPException) as excinfo:
        await qs.update_file_content(
            q.id, "missing.txt", new_content="whatever", session=dummy_session
        )

    assert excinfo.value.status_code in (400, 404)
