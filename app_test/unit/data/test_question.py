import pytest
from backend_api.model.question_model import Question, Topic
from backend_api.data import question as question_service
from backend_api.data import topic as topic_service
from backend_api.data import qtype as qtype_service
from backend_api.data import language as l_service
from app_test.conftest import engine as db_session
from backend_api.utils.utils import normalize_names


# Fixtures for basic data
@pytest.fixture
def single_question_minimal():
    return {
        "title": "SomeTitle",
        "ai_generated": True,
        "isAdaptive": True,
        "createdBy": "John Doe",
        "user_id": 1,
    }


@pytest.fixture
def multiple_questions_minimal(single_question_minimal):
    data = [
        *single_question_minimal(),
        {
            "title": "QuestionTitle2",
            "ai_generated": False,
            "isAdaptive": False,
            "createdBy": "Emma Stone",
            "user_id": 2,
        },
    ]
    return data


# ----------------------
# Minimal creation (no topics)
# ----------------------
@pytest.mark.parametrize(
    "question_data",
    [
        {
            "title": "SomeTitle",
            "ai_generated": True,
            "isAdaptive": True,
            "createdBy": "John Doe",
            "user_id": 1,
        },
        {
            "title": "QuestionTitle2",
            "ai_generated": False,
            "isAdaptive": False,
            "createdBy": "Emma Stone",
            "user_id": 2,
        },
    ],
)
def test_question_creation_minimal(db_session, question_data):
    q = Question(
        title=question_data["title"],
        ai_generated=question_data["ai_generated"],
        isAdaptive=question_data["isAdaptive"],
        createdBy=question_data["createdBy"],
        user_id=question_data["user_id"],
    )

    created = question_service.create_question(q, db_session)

    assert created.id is not None
    assert created.title == q.title
    assert created.ai_generated == q.ai_generated
    assert created.isAdaptive == q.isAdaptive
    assert created.user_id == q.user_id


# Getting all questions
@pytest.mark.parametrize(
    "question_data",
    [
        {
            "title": "SomeTitle",
            "ai_generated": True,
            "isAdaptive": True,
            "createdBy": "John Doe",
            "user_id": 1,
        },
        {
            "title": "QuestionTitle2",
            "ai_generated": False,
            "isAdaptive": False,
            "createdBy": "Emma Stone",
            "user_id": 2,
        },
    ],
)
def test_get_all_questions(db_session, question_data: dict):
    questions = question_service.get_all_questions(db_session)

    assert isinstance(questions, list)
    assert all(isinstance(q, Question) for q in questions)
    assert any(q.title == question_data["title"] for q in questions)


# Test Deleting questions
def test_delete_all_questions(db_session):
    question_service.delete_all_questions(db_session)

    questions = question_service.get_all_questions(db_session)
    assert isinstance(questions, list)
    assert questions == []


@pytest.mark.parametrize(
    "question_data",
    [
        {
            "title": "SomeTitle",
            "ai_generated": True,
            "isAdaptive": True,
            "createdBy": "John Doe",
            "user_id": 1,
        },
        {
            "title": "QuestionTitle2",
            "ai_generated": False,
            "isAdaptive": False,
            "createdBy": "Emma Stone",
            "user_id": 2,
        },
    ],
)
def test_delete_single(db_session, question_data):
    q = Question(
        title=question_data["title"],
        ai_generated=question_data["ai_generated"],
        isAdaptive=question_data["isAdaptive"],
        createdBy=question_data["createdBy"],
        user_id=question_data["user_id"],
    )
    created = question_service.create_question(q, db_session)

    assert created.id is not None
    assert created.title == q.title
    assert created.ai_generated == q.ai_generated
    assert created.isAdaptive == q.isAdaptive
    assert created.user_id == q.user_id

    question_service.delete_question_by_id(created.id, db_session)
    retrieved_q = question_service.get_question_by_id(created.id, db_session)
    assert retrieved_q == None


# ----------------------
# Unknown topics -> raises
# ----------------------
@pytest.mark.parametrize(
    "question_data",
    [
        pytest.param(
            {
                "title": "SomeTitle",
                "ai_generated": True,
                "isAdaptive": True,
                "createdBy": "John Doe",
                "user_id": 1,
                "topics": ["topic1", "topic2"],  # not created -> should error
            },
            id="unknown-topic-names",
        ),
    ],
)
def test_question_creation_error_unknown_topics(db_session, question_data):
    # Ensure clean slate
    topic_service.delete_all_topics(db_session)

    # Pass a dict payload so the service can validate/resolve topics
    with pytest.raises(ValueError, match=r"(?i)unknown topic"):
        question_service.create_question(
            question_data, db_session
        )  # create=False by default


# ----------------------
# create=True -> auto-creates missing topics
# ----------------------
def test_question_creation_creates_missing_topics_when_flag_true(db_session):
    topic_service.delete_all_topics(db_session)

    payload = {
        "title": "AutoCreate",
        "ai_generated": True,
        "isAdaptive": False,
        "createdBy": "Alice",
        "user_id": 1,
        "topics": ["topic1", "topic2"],
    }

    created = question_service.create_question(payload, db_session, create=True)

    assert created.id is not None

    # topics attached and normalized (stored lowercase)
    names = {t.name for t in created.topics}
    assert names == {"topic1", "topic2"}

    # topics exist in DB (no duplicates)
    db_names = {t.name for t in topic_service.list_topics(db_session)}
    assert db_names == {"topic1", "topic2"}


def test_get_question_topics_returns_expected_topics(db_session):
    # Arrange: clean slate
    topic_service.delete_all_topics(db_session)
    question_service.delete_all_questions(db_session)

    payload = {
        "title": "AutoCreate",
        "ai_generated": True,
        "isAdaptive": False,
        "createdBy": "Alice",
        "user_id": 1,
        "topics": ["topic1", "topic2"],
    }
    created = question_service.create_question(payload, db_session, create=True)

    # Act
    q_topics = question_service.get_question_topics(created.id, db_session)

    # Assert: type + contents
    assert isinstance(q_topics, list)
    assert all(isinstance(t, Topic) for t in q_topics)

    names = {t.name for t in q_topics}
    assert names == {"topic1", "topic2"}  # exact match, order-independent

    # Ensure they also exist in DB
    for name in names:
        assert topic_service.get_topic_by_name(db_session, name) is not None


# Test Qtype relationsjhip
def test_question_creation_creates_missing_qtypes_when_flag_true(db_session):
    qtype_service.delete_all_qtypes(db_session)

    payload = {
        "title": "AutoCreate",
        "ai_generated": True,
        "isAdaptive": False,
        "createdBy": "Alice",
        "user_id": 1,
        "qtype": ["Numerical", "MultipleChoice"],
    }

    created = question_service.create_question(payload, db_session, create=True)

    assert created.id is not None

    # topics attached and normalized (stored lowercase)
    names = {t.name.strip().lower() for t in created.qtypes}
    assert names == set(normalize_names(payload["qtype"]))

    # topics exist in DB (no duplicates)
    db_names = {t.name for t in qtype_service.list_qtypes(db_session)}
    assert db_names == set(normalize_names(payload["qtype"]))


# Test Language Relationships
def test_question_creation_creates_missing_languages_when_flag_true(db_session):
    qtype_service.delete_all_qtypes(db_session)

    payload = {
        "title": "AutoCreate",
        "ai_generated": True,
        "isAdaptive": False,
        "createdBy": "Alice",
        "user_id": 1,
        "languages": ["python", "Javascript"],
    }

    created = question_service.create_question(payload, db_session, create=True)

    assert created.id is not None

    # topics attached and normalized (stored lowercase)
    names = {t.name.strip().lower() for t in created.languages}
    assert names == set(normalize_names(payload["languages"]))

    # topics exist in DB (no duplicates)
    db_names = {t.name for t in l_service.list_languages(db_session)}
    assert db_names == set(normalize_names(payload["languages"]))


# Test updating
def test_updating_question_multiple_fields(db_session):
    # Arrange: clean slate
    topic_service.delete_all_topics(db_session)
    question_service.delete_all_questions(db_session)

    payload = {
        "title": "AutoCreate",
        "ai_generated": True,
        "isAdaptive": False,
        "createdBy": "Alice",
        "user_id": 1,
        "topics": ["topic1", "topic2"],
    }
    created = question_service.create_question(payload, db_session, create=True)
    assert created.title == payload["title"]

    original_topics = {t.name for t in created.topics}

    # Act 1: update several fields at once
    updated = question_service.update_question(
        db_session,
        question_id=created.id,
        title="NewTitle",
        isAdaptive=True,
        ai_generated=False,
        createdBy="Bob",
    )

    # Assert after first update
    assert updated.id == created.id
    assert updated.title == "NewTitle"
    assert updated.isAdaptive is True
    assert updated.ai_generated is False
    assert updated.createdBy == "Bob"
    assert {t.name for t in updated.topics} == original_topics  # topics unchanged

    # Act 2: another update (different fields)
    updated2 = question_service.update_question(
        db_session,
        question_id=created.id,
        title="FinalTitle",
        createdBy="Carol",
    )

    # Assert after second update
    assert updated2.id == created.id
    assert updated2.title == "FinalTitle"
    assert updated2.createdBy == "Carol"
    # prior boolean changes persist
    assert updated2.isAdaptive is True
    assert updated2.ai_generated is False
    assert {t.name for t in updated2.topics} == original_topics


# Test Filtering
def test_question_filtering(db_session):
    # Arrange: clean slate
    topic_service.delete_all_topics(db_session)
    question_service.delete_all_questions(db_session)

    q1 = question_service.create_question(
        {
            "title": "AutoCreate",
            "ai_generated": True,
            "isAdaptive": False,
            "createdBy": "Alice",
            "user_id": 1,
            "topics": ["topic1", "topic2"],
        },
        db_session,
        create=True,
    )

    q2 = question_service.create_question(
        {
            "title": "Other Question",
            "ai_generated": False,
            "isAdaptive": True,
            "createdBy": "Bob",
            "user_id": 2,
            "topics": ["topic3"],
        },
        db_session,
        create=True,
    )

    # AND across keys: title + ai_generated + topic name
    res = question_service.filter_questions(
        db_session, title="autocreate", ai_generated=True, topics="topic1"
    )
    assert isinstance(res, list)
    assert {r.id for r in res} == {q1.id}
    assert all("autocreate" in r.title.lower() for r in res)
    assert all(r.ai_generated is True for r in res)
    assert all(any(t.name == "topic1" for t in r.topics) for r in res)

    # OR within a single key (topics): either topic1 OR topic3
    res_or = question_service.filter_questions(db_session, topics=["topic1", "topic3"])
    assert {r.id for r in res_or} == {q1.id, q2.id}

    # Negative case: no match when AND condition fails
    res_none = question_service.filter_questions(
        db_session, title="AutoCreate", ai_generated=False
    )
    assert res_none == []
