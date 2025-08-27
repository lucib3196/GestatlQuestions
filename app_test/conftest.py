import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine
from backend_api.data import question_db as question_service
from backend_api.data import topic_db as topic_service
from backend_api.data import language_db as language_service
from backend_api.data import qtype_db as qtype_service

TEST_DB_URL = "sqlite:///:memory:"


# This creates a temporary database for the test sessions
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


# Deletes all the data in the database after reuse
@pytest.fixture(autouse=True)
def _clean_db(db_session):
    yield
    question_service.delete_all_questions(db_session)
    topic_service.delete_all_topics(db_session)
    language_service.delete_all_languages(db_session)
    qtype_service.delete_all_qtypes(db_session)



