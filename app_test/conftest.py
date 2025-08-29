# Third-party
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine, Session

# Local
from backend_api.data import language_db as language_service
from backend_api.data import qtype_db as qtype_service
from backend_api.data import question_db as question_service
from backend_api.data import topic_db as topic_service
from backend_api.data.database import Base, get_db
from backend_api.main import app


@pytest.fixture
def prepare_db():
    TEST_DB_URL = "sqlite:///:memory:"
    # Create the sqlalchemy database for testing
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create a sessionmaker to manage sessions
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create the tables in the database
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db_session(prepare_db):
    """Create a new database session with a rollback at the end of the test."""
    with Session(prepare_db.engine) as session:
        try:
            print("Session Created Successfully")
            yield session
        finally:
            session.close()
            print("Closing Database")


@pytest.fixture(scope="function")
def test_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


# Deletes all the data in the database after reuse
@pytest.fixture(autouse=True)
def _clean_db(request):
    if "db_session" not in request.fixturenames:
        yield
        return

    db_session = request.getfixturevalue("db_session")
    yield

    question_service.delete_all_questions(db_session)
    topic_service.delete_all_topics(db_session)
    language_service.delete_all_languages(db_session)
    qtype_service.delete_all_qtypes(db_session)
