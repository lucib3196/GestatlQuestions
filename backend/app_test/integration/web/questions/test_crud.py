from uuid import uuid4
from src.api.core import logger
from src.utils import pick
from src.api.models.models import Question
import pytest

QUESTION_KEYS = [
    "title",
    "ai_generated",
    "isAdaptive",
]
ADDTIONAL_METAKEYS = ["topics", "languages", "qtypes"]


def validate_response_payload(payload: dict, created: dict, key: str) -> bool:
    """Compare a given key in the request payload and response payload."""
    return pick(payload, key) == pick(created, key)


@pytest.fixture
def create_question_and_return_question(create_question_web):
    resp = create_question_web
    body = resp.json()
    qcreated = Question.model_validate(body)
    assert resp.status_code == 200
    qcreated = Question.model_validate(body)
    return qcreated


def test_create_question_response(question_payload, create_question_web):
    """Ensure a valid question payload creates a question successfully."""
    resp = create_question_web

    body = resp.json()
    logger.info("This is the body %s", body)

    assert resp.status_code == 200

    qcreated = Question.model_validate(body)
    # Validate core keys
    assert qcreated
    for k in QUESTION_KEYS:
        assert validate_response_payload(question_payload, qcreated.model_dump(), k)


def test_create_question_bad_response(create_question_bad_payload_response):
    """Ensure an invalid payload returns a 400 error with proper message."""
    resp = create_question_bad_payload_response
    body = resp.json()

    assert resp.status_code == 400
    assert "Invalid or missing input when creating question" in body["detail"]


def test_create_multiple_questions(test_client, multi_payload_questions):
    """Ensure multiple question payloads can be created sequentially."""
    for p in multi_payload_questions:
        response = test_client.post("/questions/", json=p)
        assert response.status_code == 200


# Retrieval Test
def test_get_question_bad_id(test_client):
    bad_id = uuid4()
    r = test_client.get(f"/questions/{bad_id}")
    assert r.status_code == 404


# Deletion Test
def test_delete_question(test_client, create_question_and_return_question):
    qid = create_question_and_return_question.id
    response = test_client.delete(f"/questions/{qid}")
    logger.debug(f"This is the response {response.json()}")
    assert response.status_code == 200
    assert "Deleted".lower() in response.json()["detail"].lower()

    # Try getting the data
    response = test_client.get(f"/{qid}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_question_not_valid_id(test_client):
    bad_id = uuid4()
    response = test_client.delete(f"/questions/{bad_id}")
    assert response.status_code == 404
    assert "not exist" in response.json()["detail"]

