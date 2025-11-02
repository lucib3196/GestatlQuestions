import pytest
import json


@pytest.fixture
def qpayload_bad():
    return {"Data": "Some Content"}


@pytest.fixture
def question_payload():
    """Minimal question payload with required fields only."""
    return {
        "title": "SomeTitle",
        "ai_generated": True,
        "isAdaptive": True,
    }


@pytest.fixture
def create_question_web(test_client, question_payload):
    """POST a minimal valid question payload to /questions/."""
    return test_client.post("/questions/", json=question_payload)


@pytest.fixture
def create_question_bad_payload_response(test_client, qpayload_bad):
    """POST an invalid question payload to /questions/."""
    return test_client.post("/questions/", json=qpayload_bad)
