import pytest
from src.app_test.unit.service.conftest import *
from src.api.service import question_storage_service as qs
from starlette import status
import json
from typing import List
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_returns_existing_local_path(
    monkeypatch, tmp_path, patch_questions_path, session
):
    # Arrange: question already has a valid local_path
    existing = tmp_path / "already-there"
    existing.mkdir(parents=True)
    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))

    # stub qc in the module under test
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    # Act
    resp = await qs.set_directory(q.id, session)

    # Assert
    assert resp.status == status.HTTP_200_OK
    assert "already set" in resp.detail.lower()
    assert resp.data == str(existing)
    assert session.committed is False  # no write needed
    assert session.refreshed is False


@pytest.mark.asyncio
async def test_create_new_directory_not_set(
    monkeypatch, tmp_path, patch_questions_path, session
):
    q = FakeQuestion(id=uuid4(), title="New Question", local_path=None)
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    resp = await qs.set_directory(q.id, session)

    assert resp.status == status.HTTP_201_CREATED
    assert "created successfully" in resp.detail.lower()
    created_path = resp.data
    assert created_path  # string
    assert (patch_questions_path / qs.safe_name(str(q.title))).exists()
    assert session.committed is True
    assert session.refreshed is True
    # also check Question was updated
    assert q.local_path == created_path


@pytest.mark.asyncio
async def test_name_collision_append_id(monkeypatch, patch_questions_path, session):
    fixed_uuid = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    title = "Duplicate"
    base = patch_questions_path / qs.safe_name(title)

    base.mkdir(parents=True)

    q = FakeQuestion(id=fixed_uuid, title=title, local_path=None)
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    resp = await qs.set_directory(q.id, session)
    assert resp.status == status.HTTP_201_CREATED
    expected = patch_questions_path / qs.safe_name(f"{title}_{fixed_uuid}")
    assert expected.exists()
    assert resp.data == str(expected.resolve())


@pytest.mark.asyncio
async def test_get_directory(monkeypatch, tmp_path, patch_questions_path, session):
    # Arrange: question already has a valid local_path
    existing = tmp_path / "already-there"
    existing.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    resp = await qs.get_question_directory(
        session,
        q.id,
    )
    assert resp.status == status.HTTP_200_OK
    assert "already set" in resp.detail.lower()
    assert resp.data == str(existing)
    assert session.committed is False  # no write needed
    assert session.refreshed is False


@pytest.mark.asyncio
async def test_write_files(monkeypatch, tmp_path, patch_questions_path, session):
    # Arrange: question already has a valid local_path
    existing = tmp_path / "already-there"
    existing.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    files_data = [
        qs.FileData(filename="readme.txt", content="hello"),
        qs.FileData(filename="config.json", content={"env": "dev", "debug": True}),
    ]
    resp = await qs.write_files_to_directory(
        question_id=q.id, files_data=files_data, session=session
    )
    base_dir = Path(str(q.local_path)).resolve()
    assert base_dir == existing.resolve()

    # Files written correctly
    assert (existing / "readme.txt").read_text(encoding="utf-8") == "hello"
    cfg = json.loads((existing / "config.json").read_text(encoding="utf-8"))
    assert cfg == {"env": "dev", "debug": True}


@pytest.mark.asyncio
async def test_get_files(monkeypatch, tmp_path, patch_questions_path, session):
    # Arrange: question already has a valid local_path
    existing = tmp_path / "already-there"
    existing.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    files_data = [
        qs.FileData(filename="readme.txt", content="hello"),
        qs.FileData(filename="config.json", content={"env": "dev", "debug": True}),
    ]
    # Write the files
    await qs.write_files_to_directory(
        question_id=q.id, files_data=files_data, session=session
    )

    response = await qs.get_files_from_directory(q.id, session=session)
    assert len(response.files) == len(files_data)


@pytest.mark.asyncio
async def test_get_filename(monkeypatch, tmp_path, patch_questions_path, session):
    # Arrange: question already has a valid local_path
    existing = tmp_path / "already-there"
    existing.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    files_data: List[qs.FileData] = [
        qs.FileData(filename="readme.txt", content="hello"),
        qs.FileData(filename="config.json", content={"env": "dev", "debug": True}),
    ]
    # Write the files
    await qs.write_files_to_directory(
        question_id=q.id, files_data=files_data, session=session
    )

    for f in files_data:
        r = await qs.get_file_path(
            question_id=q.id, filename=f.filename, session=session
        )

        assert r.data

        content = Path(r.data).read_text()
        c = f.content
        if isinstance(f.content, dict):
            c = json.dumps(c)
        assert content == c


@pytest.mark.asyncio
async def test_get_filename_empty(monkeypatch, tmp_path, patch_questions_path, session):
    # Arrange: question already has a valid local_path
    existing = tmp_path / "already-there"
    existing.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    with pytest.raises(HTTPException) as excinfo:
        await qs.get_file_path(q.id, filename="NotExist.txt", session=session)
    assert excinfo.value.status_code == 400


@pytest.mark.asyncio
async def test_update_file(monkeypatch, tmp_path, patch_questions_path, session):
    # Arrange: question already has a valid local_path
    existing = tmp_path / "already-there"
    existing.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))
    files_data: List[qs.FileData] = [
        qs.FileData(filename="readme.txt", content="hello"),
        qs.FileData(filename="config.json", content={"env": "dev", "debug": True}),
    ]
    # Write the files
    await qs.write_files_to_directory(
        question_id=q.id, files_data=files_data, session=session
    )
    for f in files_data:
        new_content = "New Content"
        r = await qs.update_file_content(
            q.id, f.filename, new_content=new_content, session=session
        )
        c = Path(str(r.data)).read_text()
        assert c == new_content


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fname,new_content,expect_reader",
    [
        # plain text replacement
        ("readme.txt", "New Content", lambda p: Path(p).read_text()),
        # dict should be JSON-serialized; compare via json.loads to avoid whitespace issues
        (
            "config.json",
            {"env": "prod", "debug": False},
            lambda p: json.loads(Path(p).read_text()),
        ),
        # bytes content
        ("binary.bin", b"\x00\x01\x02\x03", lambda p: Path(p).read_bytes()),
        # safe-name normalization (spaces -> underscores etc.)
        ("notes with spaces.md", " spaced ok ", lambda p: Path(p).read_text()),
    ],
)
async def test_update_file_happy_paths(
    monkeypatch,
    tmp_path,
    patch_questions_path,
    session,
    fname,
    new_content,
    expect_reader,
):
    """
    Ensure update_file_content overwrites existing file contents correctly for
    str, dict->JSON, and bytes, and respects safe filename normalization.
    """
    # Arrange: question already has a valid local_path
    existing_dir = tmp_path / "already-there"
    existing_dir.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="My Question", local_path=str(existing_dir))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    # Prime the directory with an initial version of the file
    initial = "hello" if not isinstance(new_content, (bytes, bytearray)) else b"hello"
    (
        (existing_dir / qs.safe_name(fname)).write_text(initial)
        if isinstance(initial, str)
        else (existing_dir / qs.safe_name(fname)).write_bytes(initial)
    )

    # Act: update content
    resp = await qs.update_file_content(
        q.id, fname, new_content=new_content, session=session
    )

    # Assert response basics
    assert resp.status == 200, f"Unexpected status: {resp}"
    assert isinstance(resp.data, (str, Path)), "response.data must be path-like"

    # Assert persisted content
    persisted = expect_reader(resp.data)
    if isinstance(new_content, dict):
        # For dicts, compare as objects
        assert persisted == new_content
    else:
        # For bytes/str, direct equality
        assert persisted == new_content

    # Sanity: file lives under the safe-named location
    target = existing_dir / qs.safe_name(fname)
    assert target.exists(), "Updated file should exist at normalized path"
    # And resp.data should point to that file
    assert Path(resp.data).resolve() == target.resolve()


@pytest.mark.asyncio
async def test_update_file_nonexistent_raises(monkeypatch, tmp_path, session):
    """
    Updating a file that doesn't exist should raise an HTTPException (404/400).
    """
    base = tmp_path / "empty-dir"
    base.mkdir(parents=True)

    q = FakeQuestion(id=uuid4(), title="Ghost Q", local_path=str(base))
    monkeypatch.setattr(qs, "qc", make_qc_stub(q))

    with pytest.raises(Exception) as ei:
        await qs.update_file_content(
            q.id, "missing.txt", new_content="whatever", session=session
        )

    # Accept either 404 or 400 depending on your implementation
    msg = str(ei.value)
    assert "404" in msg or "400" in msg or "not exist" in msg.lower()
