# tests/unit/service/test_question_crud_service.py

import uuid
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi import HTTPException

from backend_api.data import topic as topic_service
from backend_api.model.question_model import Question
from backend_api.service import question_crud as qcrud_service
from backend_api.utils.general_utils import names, normset
from app_test.conftest import engine as db_session

# Only scalar fields to compare directly
SCALAR_FIELDS = {"title", "ai_generated", "isAdaptive", "createdBy", "user_id"}


# ---------------------------
# Create
# ---------------------------


@pytest.mark.asyncio
async def test_create_question_minimal(
    db_session, mixed_question_payloads, invalid_question_payloads
):
    # ✅ valid payloads (dict + Question model + full dict with rels)
    for payload in mixed_question_payloads:
        created = await qcrud_service.create_question(payload, db_session)

        # Compare scalar fields only
        if isinstance(payload, Question):
            expected = payload.model_dump(include=SCALAR_FIELDS)
        else:
            expected = {k: v for k, v in payload.items() if k in SCALAR_FIELDS}

        assert created.model_dump(include=SCALAR_FIELDS) == expected
        assert isinstance(created.id, UUID)

        # Compare relationships only when provided in a dict payload
        if not isinstance(payload, Question):
            if "topics" in payload:
                assert names(created.topics) == normset(payload["topics"])
            if "languages" in payload:
                assert names(created.languages) == normset(payload["languages"])
            if "qtype" in payload:
                # adjust if your schema uses single qtype instead of list
                assert names(created.qtypes) == normset(payload["qtype"])

    # ❌ invalid payloads
    for bad in invalid_question_payloads:
        with pytest.raises(HTTPException) as excinfo:
            await qcrud_service.create_question(bad, db_session)
        assert excinfo.value.status_code == 400
        assert "Question must either be object of type Question or dict" in str(
            excinfo.value.detail
        )


# ---------------------------
# Read
# ---------------------------


@pytest.mark.asyncio
async def test_get_all_questions_empty(db_session):
    # When DB has no questions
    with pytest.raises(HTTPException) as excinfo:
        await qcrud_service.get_all_questions(db_session)
    assert excinfo.value.status_code == 204
    assert "No Questions in DB" in str(excinfo.value.detail)


@pytest.mark.asyncio
async def test_get_all_questions(db_session, seed_questions, mixed_question_payloads):
    results = await qcrud_service.get_all_questions(db_session)
    assert len(results) == len(mixed_question_payloads)  # seeded 3


@pytest.mark.asyncio
async def test_get_question_by_id(db_session, question_payload_minimal_dict):
    # Not found
    with pytest.raises(HTTPException) as excinfo:
        await qcrud_service.get_question_by_id(uuid.uuid4(), db_session)
    assert excinfo.value.status_code == 204
    assert "Question does not exist" in str(excinfo.value.detail)

    # Bad UUID
    with pytest.raises(HTTPException) as excinfo:
        await qcrud_service.get_question_by_id("not-a-uuid", db_session)
    assert excinfo.value.status_code == 400
    assert "Bad Request" in str(excinfo.value.detail) or "Invalid UUID format" in str(
        excinfo.value.detail
    )

    # Happy path
    created = await qcrud_service.create_question(
        question_payload_minimal_dict, db_session
    )
    fetched = await qcrud_service.get_question_by_id(created.id, db_session)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == created.title == question_payload_minimal_dict["title"]


# ---------------------------
# Delete
# ---------------------------


@pytest.mark.asyncio
async def test_delete_all_questions(seed_questions, db_session):
    # Ensure seeded
    assert await qcrud_service.get_all_questions(db_session)

    # Delete all
    await qcrud_service.delete_all_questions(db_session)

    # Now empty
    with pytest.raises(HTTPException) as excinfo:
        await qcrud_service.get_all_questions(db_session)
    assert excinfo.value.status_code == 204
    assert "No Questions in DB" in excinfo.value.detail


@pytest.mark.asyncio
async def test_delete_question_by_id(db_session, seed_questions):
    # Not found
    with pytest.raises(HTTPException) as excinfo:
        await qcrud_service.delete_question_by_id(uuid.uuid4(), db_session)
    assert excinfo.value.status_code == 400

    # Bad UUID
    with pytest.raises(HTTPException) as excinfo:
        await qcrud_service.delete_question_by_id("bad-uuid", db_session)
    assert excinfo.value.status_code == 400
    assert "Bad Request" in str(excinfo.value.detail) or "Invalid UUID format" in str(
        excinfo.value.detail
    )

    # Delete all seeded one-by-one
    for q in await qcrud_service.get_all_questions(db_session):
        detail = await qcrud_service.delete_question_by_id(q.id, db_session)
        assert "Question Deleted" in str(detail.get("detail"))

    # Confirm empty
    with pytest.raises(HTTPException) as excinfo:
        await qcrud_service.get_all_questions(db_session)
    assert excinfo.value.status_code == 204


# ---------------------------
# Update
# ---------------------------


@pytest.mark.asyncio
async def test_update_question_meta(db_session, question_payload_minimal_dict):
    # Clean slate for topics to avoid collisions
    topic_service.delete_all_topics(db_session)

    created = await qcrud_service.create_question(
        question_payload_minimal_dict, db_session
    )
    qid = created.id

    # Update scalar
    updated = await qcrud_service.edit_question_meta(
        qid, session=db_session, title="New Title"
    )
    assert updated.id == qid
    assert updated.title == "New Title"

    # Update relationship with strings (resolve/create + attach)
    updated = await qcrud_service.edit_question_meta(
        qid, session=db_session, topics=["New Topic", " AnotherTopic  "]
    )
    assert {t.name for t in updated.topics} == {
        "new topic",
        "anothertopic",
    }  # adapt if no normalization
    assert {t.name for t in topic_service.list_topics(db_session)}.issuperset(
        {"new topic", "anothertopic"}
    )
    # Scalar change persists
    assert updated.title == "New Title"


# ---------------------------
# Filter
# ---------------------------


@pytest.mark.asyncio
async def test_filter_questions_meta(db_session, seed_questions):
    """
    Seeded data:
      - Question model instance: isAdaptive=True, ai_generated=False
      - Minimal dict:            isAdaptive=True, ai_generated=True
      - Full dict (with rels):   isAdaptive=True, ai_generated=True
    So filtering ai_generated=False should return exactly 1.
    """
    # Filter by scalar (AND across keys in your implementation)
    only_false = await qcrud_service.filter_questions_meta(
        db_session, ai_generated=False
    )
    assert isinstance(only_false, list)
    assert len(only_false) == 1
    assert only_false[0].ai_generated is False

    # Filter by title substring (case-insensitive, depends on your filter logic)
    titled = await qcrud_service.filter_questions_meta(db_session, title="SomeTitle")
    assert all("sometitle" in q.title.lower() for q in titled)

    # Filter by relationship name (expects your filter to support .any on Topic.name)
    with_topics = await qcrud_service.filter_questions_meta(
        db_session, topics=["Topic1", "topic2"]
    )
    # At least the full dict question should match (has both Topic1/Topic2); depending on OR/AND within-key,
    # this may include others. We assert that at least one has one of those topics.
    assert any(
        any(t.name in {"topic1", "topic2"} for t in q.topics) for q in with_topics
    )


# ===========================
# Fixtures
# ===========================
@pytest.fixture
def question_payload_minimal_dict():
    return {
        "title": "SomeTitle",
        "ai_generated": True,
        "isAdaptive": True,
        "createdBy": "John Doe",
        "user_id": 1,
    }


@pytest.fixture
def question_payload_full_dict():
    return {
        "title": "SomeTitle",
        "ai_generated": True,
        "isAdaptive": True,
        "createdBy": "John Doe",
        "user_id": 1,
        "topics": ["Topic1", "Topic2"],
        "qtype": ["Numerical", "Matrix"],
        "languages": ["Python", "Go", "Rust"],
    }


@pytest.fixture
def question_instance_minimal():
    return Question(
        title="TestQuestion",
        ai_generated=False,  # distinct from the dict payloads
        isAdaptive=True,
        createdBy="Luciano",
        user_id=5,
    )


@pytest.fixture
def mixed_question_payloads(
    question_payload_minimal_dict, question_instance_minimal, question_payload_full_dict
):
    """Mix of a model instance, a minimal dict, and a full dict (with relationships)."""
    return [
        question_instance_minimal,
        question_payload_minimal_dict,
        question_payload_full_dict,
    ]


@pytest_asyncio.fixture
async def seed_questions(db_session, mixed_question_payloads):
    """Create the mixed payloads in the DB for read/filter/delete tests."""
    for payload in mixed_question_payloads:
        await qcrud_service.create_question(payload, db_session)


@pytest.fixture
def invalid_question_payloads():
    # Values that should NOT work
    return [
        "question_data",
        ["A list of values of question data"],
        123,
        None,
    ]
