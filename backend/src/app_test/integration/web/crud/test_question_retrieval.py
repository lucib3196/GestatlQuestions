# --- Standard Library ---
import json
from typing import List

# --- Third-Party ---
import pytest

# --- Internal ---
from src.api.core import logger
from src.utils.test_utils import prepare_file_uploads
from src.api.response_models import FileData


QUESTION_KEYS = ["title", "ai_generated", "isAdaptive", "createdBy"]


@pytest.mark.parametrize("payload_fixture", ["qpayload_min"])
@pytest.mark.parametrize("additional_metadata", ["", "question_additional_metadata"])
def test_question_metadata_retrieval(
    request, test_client, db_session, payload_fixture, additional_metadata
):
    """
    Integration test: create a question with optional metadata and ensure retrieval works.

    - Uses a minimal valid payload (`qpayload_min`).
    - Runs twice: once with no metadata, and once with valid `question_additional_metadata`.
    - Valid creation should return 201 Created and allow retrieval of the created question.
    """
    # Arrange
    payload = request.getfixturevalue(payload_fixture)
    metadata = (
        request.getfixturevalue(additional_metadata) if additional_metadata else None
    )

    data = {"question": json.dumps(payload)}
    if metadata:
        data["additional_metadata"] = json.dumps(metadata)

    # Act: create the question
    create_resp = test_client.post("/questions/", data=data)
    assert create_resp.status_code == 201, create_resp.text
    body = create_resp.json()
    question_id = body["question"]["id"]

    logger.debug("Created question body: %s", body)

    # Act: retrieve the question
    retrieved_resp = test_client.get(f"/questions/{question_id}")
    assert retrieved_resp.status_code == 200, retrieved_resp.text
    retrieved_body = retrieved_resp.json()
    retrieved_question = retrieved_body["question"]

    logger.debug("Retrieved question: %s", retrieved_question)

    # Assert: ensure core fields match
    assert retrieved_question
    for key in QUESTION_KEYS:
        assert retrieved_question.get(key) == payload.get(key)


# File Retrieval
@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
def test_list_question_files(
    request, test_client, db_session, qpayload_min, file_fixture
):
    """
    Ensure that uploaded files for a question are listed correctly.
    """
    # Arrange: create a question with uploaded files
    data = {"question": json.dumps(qpayload_min)}
    files_data = request.getfixturevalue(file_fixture)
    files = prepare_file_uploads(files_data)
    creation_resp = test_client.post("/questions/", data=data, files=files)

    body = creation_resp.json()
    qid = body["question"]["id"]

    logger.debug("Created question: %s", body["question"])

    # Act: retrieve the list of files
    retrieval_resp = test_client.get(f"/questions/{qid}/files")
    retrieved_files = retrieval_resp.json()

    logger.debug("Retrieved files: %s", retrieved_files)

    # Assert
    assert retrieval_resp.status_code == 200
    assert len(retrieved_files) == len(files)


@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
def test_list_question_files_data(
    request, test_client, db_session, qpayload_min, file_fixture
):
    """
    Ensure that uploaded files are returned with their data (filename + content).
    """
    # Arrange
    data = {"question": json.dumps(qpayload_min)}
    files_data = request.getfixturevalue(file_fixture)
    files = prepare_file_uploads(files_data)
    creation_resp = test_client.post("/questions/", data=data, files=files)

    body = creation_resp.json()
    qid = body["question"]["id"]

    logger.debug("Created question: %s", body["question"])

    # Act
    retrieval_resp = test_client.get(f"/questions/{qid}/files_data")
    retrieved_files = retrieval_resp.json()

    # Assert
    assert retrieval_resp.status_code == 200
    assert len(retrieved_files) == len(files)


@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
def test_read_question_file(
    request, test_client, db_session, qpayload_min, file_fixture
):
    """
    Ensure that each uploaded file can be retrieved individually by filename.
    """
    # Arrange
    data = {"question": json.dumps(qpayload_min)}
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


# Misc
@pytest.mark.parametrize("payload_fixture", ["qpayload_min"])
@pytest.mark.parametrize("file_fixture", ["file_data_payload", "question_file_payload"])
@pytest.mark.parametrize("additional_metadata", ["", "question_additional_metadata"])
def test_question_metadata_retrieval_full(
    request, test_client, db_session, payload_fixture, additional_metadata, file_fixture
):
    """
    Integration test: create a question with optional metadata and ensure retrieval works.

    - Uses a minimal valid payload (`qpayload_min`).
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
