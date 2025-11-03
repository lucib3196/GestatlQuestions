from uuid import uuid4
from src.api.core import logger
from src.utils import pick
from src.api.models.models import Question
from src.api.models import QuestionMeta, QuestionData
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


def retrieve_question(client, qid):
    resp = client.get(f"/questions/{qid}")
    assert resp.status_code == 200, resp.text
    response_data = resp.json()
    qretrieved = Question.model_validate(response_data)
    assert qretrieved
    return qretrieved


@pytest.fixture
def create_question_and_return_question(create_question_web):
    resp = create_question_web
    body = resp.json()
    qcreated = Question.model_validate(body)
    assert resp.status_code == 200
    qcreated = Question.model_validate(body)
    return qcreated


@pytest.fixture
def create_multiple_question_responses(test_client, multi_payload_questions):
    for p in multi_payload_questions:
        response = test_client.post("/questions/", json=p)
        assert response.status_code == 200
    return multi_payload_questions


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


def test_create_multiple_questions(create_multiple_question_responses):
    assert create_multiple_question_responses


# ------------------------
# Retrieval Test
# ------------------------
def test_question_metadata_retrieval(test_client, create_question_and_return_question):
    """
    Integration test: create a question with optional metadata and ensure retrieval works.

    - Uses a minimal valid payload (`question_payload_minimal_dict`).
    - Runs twice: once with no metadata, and once with valid `question_additional_metadata`.
    - Valid creation should return 201 Created and allow retrieval of the created question.
    """
    question_id = create_question_and_return_question.id

    # Act: retrieve the question
    retrieved = retrieve_question(test_client, question_id)

    logger.debug("Retrieved question: %s", retrieved)
    assert retrieved
    assert retrieved.id == question_id


def test_qet_all_questions(test_client, create_multiple_question_responses):
    qpayloads = create_multiple_question_responses
    offset, limit = 0, 100
    response = test_client.get(f"/questions/{offset}/{limit}")
    assert response.status_code == 200, response.text
    questions = response.json()
    logger.info("This is the response of getting all the questions %s", questions)
    assert isinstance(questions, list), "Expected response to be a list"
    assert len(questions) == len(
        qpayloads
    ), f"Expected {len(qpayloads)} questions, got {len(questions)}"
    logger.info("these are the questions %s", questions)


def test_get_all_questions_metadata(test_client, create_question_and_return_question):
    question_id = create_question_and_return_question.id
    response = test_client.get(f"/questions/{question_id}/all_data")
    assert response.status_code == 200
    question_data = response.json()
    assert QuestionMeta.model_validate(question_data)


def test_get_get_all_question_data(create_multiple_question_responses, test_client):
    # --- Arrange ---
    qpayloads = create_multiple_question_responses
    offset, limit = 0, 100

    # --- Act ---
    response = test_client.get(f"/questions/{offset}/{limit}/all_data")
    data = response.json()
    logger.info("Retrieved minimal questions response: %s", data)

    # --- Assert: Basic response validation ---
    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"

    assert isinstance(data, list), f"Expected list, got {type(data).__name__}"

    # --- Assert: Schema validation ---
    validated_questions = []
    for idx, q in enumerate(data):
        try:
            validated = QuestionMeta.model_validate(q)
            validated_questions.append(validated)
        except Exception as e:
            pytest.fail(f"Question at index {idx} failed schema validation: {e}")

    # --- Assert: Count consistency ---
    expected_count = len(qpayloads)
    actual_count = len(validated_questions)
    assert (
        actual_count == expected_count
    ), f"Expected {expected_count} questions, got {actual_count}"

    logger.info(" Retrieved %d minimal questions successfully.", actual_count)


def test_get_question_bad_id(test_client):
    bad_id = uuid4()
    r = test_client.get(f"/questions/{bad_id}")
    assert r.status_code == 404


def test_get_question_data_all_not_found(test_client):
    bad_id = uuid4()
    r = test_client.get(f"/questions/{bad_id}/all_data")
    assert r.status_code == 500


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


def test_delete_all(test_client, create_multiple_question_responses):
    qpayloads = create_multiple_question_responses
    response = test_client.delete("/questions")
    assert response.status_code == 200
    offset, limit = 0, 100
    response = test_client.get(f"/questions/{offset}/{limit}")
    retrieved = response.json()
    assert isinstance(retrieved, list), "Expected response to be a list"
    assert len(retrieved) == 0


# Updates
@pytest.mark.asyncio
async def test_filter_questions_no_match(
    test_client, create_multiple_question_responses
):
    """
    Filtering with values that should not match anything.
    Expect an empty list.
    """
    payload = QuestionData(title="NonExistent", ai_generated=True)

    response = test_client.post("/questions/filter", json=payload.model_dump())
    assert response.status_code == 200

    data = response.json()
    logger.info("Filter with no match response: %s", data)

    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_question_filter_by_title(
    test_client, create_multiple_question_responses
):
    """
    Filter questions by a substring in the title.
    Expects at least one match from create_multiple_questions fixture.
    """
    payload = QuestionData(title="Thermodynamics First Law")

    response = test_client.post("/questions/filter", json=payload.model_dump())
    assert response.status_code == 200

    data = response.json()
    logger.info("Filter by title response: %s", data)

    assert isinstance(data, list)
    assert len(data) > 0
