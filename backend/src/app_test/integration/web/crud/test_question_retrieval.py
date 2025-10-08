# --- Standard Library ---
import json
from typing import List
from uuid import UUID
from uuid import uuid4

# --- Third-Party ---
import pytest

# --- Internal ---
from src.api.core import logger
from src.utils.test_utils import prepare_file_uploads
from src.api.response_models import FileData
from src.utils.normalization_utils import to_serializable
from src.api.response_models import QuestionReadResponse


QUESTION_KEYS = ["title", "ai_generated", "isAdaptive", "createdBy"]


# Helpers
def create_question(client, payload, metadata=None):
    data = {"question": json.dumps(payload)}
    if metadata:
        data["additional_metadata"] = json.dumps(metadata)

    resp = client.post("/questions/", data=data)
    assert resp.status_code == 201, resp.text

    # Re-validate response data against the schema
    response_data = resp.json()
    validated = QuestionReadResponse.model_validate(response_data)
    assert validated

    return validated.question


def retrieve_question(client, qid):
    resp = client.get(f"/questions/{qid}")
    assert resp.status_code == 200, resp.text
    response_data = resp.json()
    validated = QuestionReadResponse.model_validate(response_data)
    assert validated
    return validated.question


@pytest.mark.parametrize("payload_fixture", ["question_payload_minimal_dict"])
@pytest.mark.parametrize("additional_metadata", ["", "question_additional_metadata"])
def test_question_metadata_retrieval(
    request, test_client, db_session, payload_fixture, additional_metadata
):
    """
    Integration test: create a question with optional metadata and ensure retrieval works.

    - Uses a minimal valid payload (`question_payload_minimal_dict`).
    - Runs twice: once with no metadata, and once with valid `question_additional_metadata`.
    - Valid creation should return 201 Created and allow retrieval of the created question.
    """
    # Arrange
    payload = request.getfixturevalue(payload_fixture)
    metadata = (
        request.getfixturevalue(additional_metadata) if additional_metadata else None
    )
    question = create_question(test_client, payload, metadata)
    question_id = question.id

    logger.debug("Created question body: %s", question)

    # Act: retrieve the question
    retrieved = retrieve_question(test_client, question_id)

    logger.debug("Retrieved question: %s", retrieved)
    assert retrieved

    # Assert: ensure core fields match
    data = retrieved.model_dump()
    for key in QUESTION_KEYS:
        assert data.get(key) == payload.get(key)


# File Retrieval
@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
def test_list_question_files(
    request, test_client, db_session, question_payload_minimal_dict, file_fixture
):
    """
    Ensure that uploaded files for a question are listed correctly.
    """
    # Arrange: create a question with uploaded files
    data = {"question": json.dumps(question_payload_minimal_dict)}
    files_data = request.getfixturevalue(file_fixture)
    files = prepare_file_uploads(files_data)
    creation_resp = test_client.post("/questions/", data=data, files=files)

    body = creation_resp.json()
    qid = body["question"]["id"]

    logger.debug("Created question: %s", body["question"])

    # Act: retrieve the list of files
    retrieval_resp = test_client.get(f"/questions/{qid}/files")
    data = retrieval_resp.json()
    retrieved_files = data.files
    logger.debug("Retrieved files: %s", retrieved_files)

    # Assert
    assert retrieval_resp.status_code == 200
    assert len(retrieved_files) == len(files)


@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
def test_list_question_files_data(
    request, test_client, db_session, question_payload_minimal_dict, file_fixture
):
    """
    Ensure that uploaded files are returned with their data (filename + content).
    """
    # Arrange
    data = {"question": json.dumps(question_payload_minimal_dict)}
    files_data = request.getfixturevalue(file_fixture)
    files = prepare_file_uploads(files_data)
    creation_resp = test_client.post("/questions/", data=data, files=files)

    body = creation_resp.json()
    qid = body["question"]["id"]

    logger.debug("Created question: %s", body["question"])

    # Act
    retrieval_resp = test_client.get(f"/questions/{qid}/files_data")
    body = retrieval_resp.json()
    retrieved_files = body.files

    # Assert
    assert retrieval_resp.status_code == 200
    assert len(retrieved_files) == len(files)


@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
def test_read_question_file(
    request, test_client, db_session, question_payload_minimal_dict, file_fixture
):
    """
    Ensure that each uploaded file can be retrieved individually by filename.
    """
    # Arrange
    data = {"question": json.dumps(question_payload_minimal_dict)}
    files_data: List[FileData] = request.getfixturevalue(file_fixture)
    files = prepare_file_uploads(files_data)
    creation_resp = test_client.post("/questions/", data=data, files=files)

    body = creation_resp.json()
    qid = body["question"]["id"]

    logger.debug("Created question: %s", body["question"])

    # Act & Assert
    for f in files_data:
        retrieval_resp = test_client.get(f"/questions/{qid}/files/{f.filename}")
        assert retrieval_resp.status_code == 200

        retrieved_content = retrieval_resp.json()

        # Normalize comparison depending on type
        if isinstance(f.content, dict):
            # API might return dict OR stringified JSON, normalize both
            if isinstance(retrieved_content, str):
                retrieved_content = json.loads(retrieved_content)
            assert retrieved_content == f.content

        elif isinstance(f.content, (bytes, bytearray)):
            # Binary content may come back base64-encoded or raw string
            if isinstance(retrieved_content, str):
                retrieved_content = retrieved_content.encode()
            assert retrieved_content == f.content

        else:
            # Assume plain text
            assert retrieved_content == f.content


# Batch get all questions
def test_get_question_data_minimal(db_session, all_question_payloads, test_client):
    """Test batch creation of questions and retrieval in minimal format."""
    # Create questions
    for q in all_question_payloads:
        data = {"question": json.dumps(to_serializable(q))}
        logger.debug("Creating question with payload: %s", data)

        creation_resp = test_client.post("/questions/", data=data)
        logger.debug("Created question response: %s", creation_resp.json())

        assert creation_resp.status_code == 201, "Question creation failed"

    # Retrieve minimal list of questions
    offset, limit = 0, 100
    response = test_client.get(f"/questions/get_all/{offset}/{limit}/minimal")

    logger.debug("Retrieved minimal questions response: %s", response.json())
    assert response.status_code == 200, "Failed to fetch minimal questions list"

    questions = response.json()
    assert isinstance(questions, list), "Expected response to be a list"
    assert len(questions) == len(
        all_question_payloads
    ), f"Expected {len(all_question_payloads)} questions, got {len(questions)}"


# Misc
@pytest.mark.parametrize("payload_fixture", ["question_payload_minimal_dict"])
@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
@pytest.mark.parametrize("additional_metadata", ["", "question_additional_metadata"])
def test_question_metadata_retrieval_full(
    request, test_client, db_session, payload_fixture, additional_metadata, file_fixture
):
    """
    Integration test: create a question with optional metadata and ensure retrieval works.

    - Uses a minimal valid payload (`question_payload_minimal_dict`).
    - Runs twice: once with no metadata, and once with valid `question_additional_metadata`.
    - Valid creation should return 201 Created and allow retrieval of the created question.
    """
    # Arrange
    payload = request.getfixturevalue(payload_fixture)
    metadata = (
        request.getfixturevalue(additional_metadata) if additional_metadata else None
    )
    files_data = request.getfixturevalue(file_fixture)
    files = prepare_file_uploads(files_data)

    data = {"question": json.dumps(payload)}
    if metadata:
        data["additional_metadata"] = json.dumps(metadata)

    # Act: create the question
    create_resp = test_client.post("/questions/", data=data, files=files)
    assert create_resp.status_code == 201, create_resp.text
    body = create_resp.json()
    question_id = body["question"]["id"]

    logger.debug("Created question body: %s", body)

    # Act: retrieve the question
    retrieved_resp = test_client.get(f"/questions/{question_id}/full")
    assert retrieved_resp.status_code == 200, retrieved_resp.text

    retrieved_body = retrieved_resp.json()
    retrieved_question = retrieved_body["question"]

    retrieved_filesdata = retrieved_body["files"]

    logger.debug("Retrieved question: %s", retrieved_question)

    # Assert: ensure core fields match
    assert retrieved_question
    for key in QUESTION_KEYS:
        assert retrieved_question.get(key) == payload.get(key)

    assert retrieved_filesdata
    retrieved_filenames = {f["filename"] for f in retrieved_filesdata}
    expected_filenames = {f.filename for f in files_data}
    assert retrieved_filenames == expected_filenames


def test_get_question_bad_id(test_client):
    bad_id = uuid4()
    r = test_client.get(f"/questions/{bad_id}")
    assert r.status_code == 404


def test_get_question_data_all_not_found(test_client):
    bad_id = uuid4()
    r = test_client.get(f"/questions/{bad_id}/full")
    assert r.status_code == 500


@pytest.mark.asyncio
async def test_question_filter_by_title(test_client, create_multiple_question):
    """
    Filter questions by a substring in the title.
    Expects at least one match from create_multiple_questions fixture.
    """
    payload = {"title": "SomeTitle"}

    response = test_client.post("/questions/filter_questions", json=payload)
    assert response.status_code == 200

    data = response.json()
    logger.info("Filter by title response: %s", data)

    assert isinstance(data, list)
    assert len(data) > 0
    for q in data:
        assert "title" in q
        assert payload["title"].lower() in q["title"].lower()


@pytest.mark.asyncio
async def test_filter_questions_by_title_and_flags(
    test_client, create_multiple_question
):
    """
    Filters by a substring in title + ai_generated + createdBy.
    Uses the questions inserted by the create_multiple_questions fixture.
    """
    payload = {
        "title": "Thermodynamics",
        "ai_generated": False,
        "createdBy": "tester_thermo",
    }

    response = test_client.post("/questions/filter_questions", json=payload)
    assert response.status_code == 200

    data = response.json()
    logger.info("Filter by title + flags response: %s", data)

    assert isinstance(data, list)
    assert len(data) >= 1

    for q in data:
        assert payload["title"].lower() in q["title"].lower()
        assert q["ai_generated"] == payload["ai_generated"]
        assert q["createdBy"] == payload["createdBy"]


@pytest.mark.asyncio
async def test_filter_questions_no_match(test_client, create_multiple_question):
    """
    Filtering with values that should not match anything.
    Expect an empty list.
    """
    payload = {
        "title": "NonExistent",
        "ai_generated": True,
        "createdBy": "ghost_user",
    }

    response = test_client.post("/questions/filter_questions", json=payload)
    assert response.status_code == 200

    data = response.json()
    logger.info("Filter with no match response: %s", data)

    assert isinstance(data, list)
    assert len(data) == 0
