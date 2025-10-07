# Stdlib
import uuid
from pathlib import Path
from src.api.core import logger

# Third-party
import pytest

# Internal
from src.api.core import logger
from src.api.service.crud import question_crud
from src.api.service.question_manager import QuestionManager
from src.app_test.conftest import FakeQuestion, DummyStorage


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def local_qm(dummy_storage):
    """Provide a QuestionManager instance backed by DummyStorage."""
    qm = QuestionManager(storage_service=dummy_storage, storage_type="local")
    logger.info("Initialized local question manager dummy %s", qm.question_dir)
    return qm


@pytest.fixture
def fake_qpayload():
    """Minimal fake payload to construct a FakeQuestion."""
    return {
        "title": "Fake",
        "local_path": None,
        "blob_name": None,
        "id": uuid.UUID("6e81a590-935b-411a-9a7d-12ec4bfb5172"),
    }


@pytest.fixture
def create_question(local_qm, dummy_session, monkeypatch, fake_qpayload):
    """Provide a factory to create fake questions."""

    async def _create_question(override_payload=None):
        payload = override_payload or fake_qpayload
        fake_question = FakeQuestion(**payload)

        async def fake_create_question(question, session):
            return fake_question

        monkeypatch.setattr(question_crud, "create_question", fake_create_question)
        return await local_qm.create_question(
            question=fake_question, session=dummy_session
        )

    return _create_question


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_initialization(local_qm, tmp_path):
    logger.info("This is the question dir %s", local_qm.question_dir)


@pytest.mark.asyncio
async def test_create_question(local_qm, tmp_path, create_question, fake_qpayload):
    # Given: a patched create_question returning a FakeQuestion
    q = await create_question()

    # When: deriving the expected local path
    basename = local_qm.get_basename()
    logger.info("Testing the create question local this is the base name %s", basename)
    expected_path = tmp_path / basename / fake_qpayload["title"]

    # Then: assertions
    assert isinstance(q, FakeQuestion)
    assert q.title == fake_qpayload["title"]
    assert q.local_path
    assert Path(q.local_path) == Path(expected_path)


@pytest.mark.asyncio
async def test_create_question_duplicate_title(
    local_qm, tmp_path, create_question, fake_qpayload
):
    q1 = await create_question()
    q2 = await create_question()

    # When: deriving the expected local path
    basename = local_qm.get_basename()
    expected_path = (
        tmp_path / basename / f'{fake_qpayload["title"]}_{fake_qpayload["id"]}'
    )
    assert Path(q2.local_path) == Path(expected_path)


@pytest.mark.asyncio
async def test_get_question_path(local_qm, tmp_path, create_question, fake_qpayload):
    q1 = await create_question()

    retrieved_path = local_qm.get_question_path(q1)
    logger.debug("This is the retrieved path %s", retrieved_path)
    basename = local_qm.get_basename()
    expected_path = tmp_path / basename / f'{fake_qpayload["title"]}'
    assert Path(retrieved_path) == Path(expected_path) == Path(q1.local_path)


@pytest.mark.asyncio
async def test_get_question_identifier(
    local_qm, tmp_path, dummy_session, monkeypatch, create_question, fake_qpayload
):
    # Given: a created fake question
    q1 = await create_question()
    q2 = await create_question()

    # Patch the dependency so it always returns q1
    async def fake_get_question_by_id(question_id, session):
        assert question_id == q1.id  # sanity check
        return q1

    async def fake_get_question_by_id2(question_id, session):
        assert question_id == q2.id
        return q2

    monkeypatch.setattr(question_crud, "get_question_by_id", fake_get_question_by_id)

    ## Check the first original instance
    # When: we call get_question_identifier
    qidentifier = await local_qm.get_question_identifier(q1.id, dummy_session)
    # Then: it should resolve to the directory name
    logger.debug("This is the identifier %s", qidentifier)
    assert qidentifier
    assert qidentifier == fake_qpayload["title"]
    assert isinstance(qidentifier, str)
    assert qidentifier == Path(q1.local_path).name

    ## Patch again but with the second instance
    monkeypatch.setattr(question_crud, "get_question_by_id", fake_get_question_by_id2)
    # When: we call get_question_identifier
    qidentifier = await local_qm.get_question_identifier(q2.id, dummy_session)
    # Then: it should resolve to the directory name
    logger.debug("This is the identifier %s", qidentifier)
    assert qidentifier
    assert qidentifier == f'{fake_qpayload["title"]}_{fake_qpayload["id"]}'
    assert isinstance(qidentifier, str)
    assert qidentifier == Path(q2.local_path).name
