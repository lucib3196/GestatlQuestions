import pytest
from src.api.database import question as qdb
from src.api.models.question import QuestionData

@pytest.fixture
def combined_payload(question_payload, question_payload_2):
    return [question_payload, question_payload_2]


@pytest.fixture
@pytest.mark.asyncio
async def create_question_with_relationship(
    db_session, question_payload, relationship_payload
):
    qdata = QuestionData(**question_payload, **relationship_payload)
    qcreated = await qdb.create_question(qdata, db_session)
    assert qcreated
    return qcreated
