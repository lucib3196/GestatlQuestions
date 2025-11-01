from src.api.database import question as qdb
import pytest
from src.utils import pick
from src.api.models.models import Topic, Language, Question, QType
from src.api.core.logging import logger
from src.api.models.question import QuestionUpdate, QuestionMeta


# ----------------------
# Minimal creation (no topics)
# ----------------------
def test_create_question(db_session, question_payload):
    qcreated = qdb.create_question(question_payload, db_session)
    assert qcreated
    for key, _ in question_payload.model_dump().items():
        assert getattr(qcreated, key) == getattr(question_payload, key)


def test_create_question_with_relationship_data(
    db_session, question_payload, relationship_payload
):
    qcreated = qdb.create_question(question_payload, db_session, relationship_payload)
    assert qcreated
    for key, _ in question_payload.model_dump().items():
        assert getattr(qcreated, key) == getattr(question_payload, key)

    for key, _ in relationship_payload.items():
        logger.info("Relationship data %s", getattr(qcreated, key))
        qrel = getattr(qcreated, key)
        # Convert to a list with just the names and set for comparing
        assert set([r.name for r in qrel]) == set(relationship_payload[key])


def test_get_question(db_session, question_payload):
    qcreated = qdb.create_question(question_payload, db_session)
    assert qcreated == qdb.get_question(qcreated.id, db_session)


def test_get_all_questions(db_session, combined_payload):
    # Create data
    for q in combined_payload:
        qcreated = qdb.create_question(q, db_session)
        assert qcreated
    questions = qdb.get_all_questions(db_session)
    assert isinstance(questions, list)
    assert all(isinstance(q, Question) for q in questions)
    assert len(combined_payload) == len(questions)


# Test Deleting questions
def test_delete_all_questions(db_session, combined_payload):
    for q in combined_payload:
        qcreated = qdb.create_question(q, db_session)
        assert qcreated
    qdb.delete_all_questions(db_session)
    questions = qdb.get_all_questions(db_session)
    assert isinstance(questions, list)
    assert questions == []


def test_delete_single(db_session, combined_payload):
    for q in combined_payload:
        qcreated = qdb.create_question(q, db_session)
        assert qcreated

        # Get the question
        assert qdb.get_question(qcreated.id, db_session)
        qdb.delete_question(qcreated.id, db_session)
        assert qdb.get_question(qcreated.id, db_session) is None


@pytest.mark.asyncio
async def test_get_question_data(create_question_with_relationship, db_session):
    qcreated = create_question_with_relationship
    data = await qdb.get_question_data(qcreated.id, db_session)
    assert data


@pytest.mark.asyncio
async def test_question_update(db_session, question_payload):

    qcreated = qdb.create_question(question_payload, db_session)
    assert qcreated is not None
    assert isinstance(qcreated, Question)

    update_data = QuestionUpdate(
        title="new title", topics=["history", "math", "science"]
    )

    qupdate = await qdb.update_question(qcreated.id, update_data, db_session)
    assert qupdate is not None
    assert isinstance(qupdate, QuestionMeta)

    assert qupdate.title == "new title"
    assert isinstance(qupdate.topics, list)
    assert len(qupdate.topics) == 3

    refetched = db_session.get(Question, qcreated.id)
    assert refetched.title == "new title"
