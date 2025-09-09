import pytest
from src.api.models import Question


@pytest.fixture
def minimal_question_payload_model():
    return Question(
        title="Sample Question",
        ai_generated=True,
        isAdaptive=False,
        createdBy="Test User",
        user_id=1,
    )


@pytest.fixture
def minimal_question_payload_dict():
    return {
        "title": "QuestionTitle2",
        "ai_generated": False,
        "isAdaptive": False,
        "createdBy": "Luci Goosey",
        "user_id": 2,
    }


@pytest.fixture
def question_payload_with_relationships():
    return {
        "title": "QuestionTitle3",
        "ai_generated": False,
        "isAdaptive": False,
        "createdBy": "Luci Goosey",
        "user_id": 2,
        "topics": ["topic1", "topic2"],
        "languages": ["language1", "language2"],
        "qtypes": ["qtype1", "qtype2"],
    }


@pytest.fixture
def combined_payload(
    minimal_question_payload_dict,
    minimal_question_payload_model,
    question_payload_with_relationships,
):
    return [
        minimal_question_payload_model,
        minimal_question_payload_dict,
        question_payload_with_relationships,
    ]
