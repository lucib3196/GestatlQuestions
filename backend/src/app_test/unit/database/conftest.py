# Third-party
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from sqlmodel import Session, create_engine, SQLModel

# Local
from src.api.database.database import Base


@asynccontextmanager
async def on_startup_test(app: FastAPI):
    # skip init_db in tests
    yield


## Setting up the database manually set to test, then
## Add a clean up function
@pytest.fixture(scope="session")
def test_engine():
    """Create a dedicated in-memory test engine."""
    url = "sqlite:///:memory:"
    engine = create_engine(
        url,
        echo=False,
        #    connect_args={"check_same_thread": False})
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Provide a new SQLModel session for each test."""
    with Session(test_engine) as session:
        yield session
        session.rollback()  # rollback ensures isolation


@pytest.fixture(autouse=True)
def _clean_db(db_session, test_engine):
    print("Cleaning database")
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)




# # Going to need to change this eentually
# @pytest.fixture(scope="function")
# def test_client(db_session):
#     """FastAPI TestClient with DB session override."""
#     app = get_application()
#     app.router.lifespan_context = on_startup_test

#     def override_get_db():
#         try:
#             yield db_session
#         finally:
#             pass  # db_session closed by fixture

#     app.dependency_overrides[get_session] = override_get_db

#     with TestClient(app) as client:
#         yield client
