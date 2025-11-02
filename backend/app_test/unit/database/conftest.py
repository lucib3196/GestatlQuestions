import pytest
from sqlmodel import Session, create_engine
from src.api.database.database import Base
from src.api.core import logger
from src.api.database.database import Base
from src.api.models.question import QuestionBase
from src.api.database import question as qdb
from src.api.models.question import QuestionData


@pytest.fixture(scope="function")
def test_engine(tmp_path):
    url = f"sqlite:///{tmp_path}/test.db"
    engine = create_engine(
        url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Provide a new SQLModel session for each test."""
    with Session(test_engine, expire_on_commit=False) as session:
        yield session
        session.rollback()  # rollback ensures isolation


@pytest.fixture(autouse=True)
def _clean_db(db_session, test_engine):
    logger.debug("Cleaning Database")
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)


@pytest.fixture
def question_payload():
    return {
        "title": "Sample Question",
        "ai_generated": True,
        "isAdaptive": False,
    }


@pytest.fixture
def question_payload_2():
    return QuestionBase(title="Question 2", ai_generated=False, isAdaptive=True)


@pytest.fixture
def relationship_payload():
    return {
        "topics": ["math", "science", "engineering"],
        "languages": ["python"],
        "qtypes": ["numerical", "multiple-choice"],
    }


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
