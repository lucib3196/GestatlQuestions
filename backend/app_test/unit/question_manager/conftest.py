import pytest
from src.api.service.question_manager import QuestionManager


@pytest.fixture(
    scope="function",
)
def question_manager(db_session):
    qm = QuestionManager(db_session)
    return qm
