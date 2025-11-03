import pytest
from src.api.models.question import QuestionBase


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
