# tests/unit/service/test_question_crud_service.py


import pytest
import pytest_asyncio


from src.api.models.question_model import Question
from src.api.service.crud import question_crud as qcrud_service
from src.utils import *


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
