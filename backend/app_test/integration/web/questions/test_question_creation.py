from src.api.core import logger
from src.utils import pick
from src.api.models.models import Question

QUESTION_KEYS = [
    "title",
    "ai_generated",
    "isAdaptive",
]
ADDTIONAL_METAKEYS = ["topics", "languages", "qtypes"]


def validate_response_payload(payload: dict, created: dict, key: str) -> bool:
    """Compare a given key in the request payload and response payload."""
    return pick(payload, key) == pick(created, key)


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
