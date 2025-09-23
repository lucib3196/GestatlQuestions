# --- Standard Library ---
import json

# --- Third-Party ---
import pytest

# --- Internal ---
from src.api.core import logger
from src.utils import pick
from src.utils.test_utils import prepare_file_uploads

# Keys of interest for minimal question validation
QUESTION_KEYS = ["title", "ai_generated", "isAdaptive", "createdBy"]
ADDTIONAL_METAKEYS = ["topics", "languages", "qtypes"]


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture
def create_question_minimal_response(test_client, db_session, qpayload_min):
    """POST a minimal valid question payload to /questions/."""
    data = {"question": json.dumps(qpayload_min)}
    return test_client.post("/questions/", data=data)


@pytest.fixture
def create_question_bad_payload_response(test_client, db_session, qpayload_bad):
    """POST an invalid question payload to /questions/."""
    data = {"question": json.dumps(qpayload_bad)}
    return test_client.post("/questions/", data=data)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def validate_response_payload(payload: dict, created: dict, key: str) -> bool:
    """Compare a given key in the request payload and response payload."""
    return pick(payload, key) == pick(created, key)


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
def test_create_question_response(create_question_minimal_response, qpayload_min):
    """Ensure a valid question payload creates a question successfully."""
    resp = create_question_minimal_response
    body = resp.json()
    logger.debug("This is the body %s", body)

    assert resp.status_code == 201
    qcreated = body["question"]

    # Validate core keys
    assert qcreated
    for k in QUESTION_KEYS:
        assert validate_response_payload(qpayload_min, qcreated, k)


def test_create_question_bad_response(create_question_bad_payload_response):
    """Ensure an invalid payload returns a 400 error with proper message."""
    resp = create_question_bad_payload_response
    body = resp.json()

    assert resp.status_code == 400
    assert "Invalid or missing input when creating question" in body["detail"]


@pytest.mark.parametrize("payload_fixture", ["qpayload_min", "qpayload_bad"])
@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
@pytest.mark.parametrize("additional_metadata", ["", "question_additional_metadata"])
def test_create_question_with_files(
    request, test_client, db_session, payload_fixture, file_fixture, additional_metadata
):
    """
    Test uploading files with different payloads.
    - Valid payloads should succeed (201).
    - Invalid payloads may raise 400, 422, or 500.
    """
    payload = request.getfixturevalue(payload_fixture)
    files_data = request.getfixturevalue(file_fixture)
    files = prepare_file_uploads(files_data)
    metadata = (
        request.getfixturevalue(additional_metadata) if additional_metadata else None
    )

    data = {"question": json.dumps(payload)}
    if metadata:
        data["additional_metadata"] = json.dumps(metadata)
    resp = test_client.post("/questions/", data=data, files=files)

    body = resp.json()

    logger.debug(
        "This is the response body %s",
    )

    if payload_fixture == "qpayload_min":
        assert resp.status_code == 201
        qcreated = body["question"]
        # Validate core keys
        assert qcreated
        for k in QUESTION_KEYS:
            assert validate_response_payload(payload, qcreated, k)
    else:
        assert resp.status_code in (400, 422, 500)



