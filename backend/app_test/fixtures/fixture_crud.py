from typing import Literal
import pytest
import pytest_asyncio


from src.api.core import logger
from src.utils import *
from src.api.models import (
    QuestionReadResponse,
    SuccessFileResponse,
    SuccessDataResponse,
)





@pytest.fixture
def question_payload_full_dict():
    """Full question payload including topics, qtypes, and languages."""
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


# --- Domain-Specific Payloads ---


@pytest.fixture
def question_payload_mechanics():
    """Mechanics/statics question payload with metadata."""
    return {
        "title": "Statics Basics",
        "ai_generated": True,
        "isAdaptive": True,
        "createdBy": "tester_mech",
        "user_id": 1,
        "topics": ["Mechanics", "Statics"],
        "languages": ["python"],
        "qtype": ["numeric"],
    }





# --- Aggregate Fixture ---


@pytest.fixture
def all_question_payloads(
    question_payload_minimal_dict,
    question_payload_full_dict,
    question_payload_mechanics,
    question_payload_thermo,
    question_payload_fluids,
):
    """
    Aggregate of all question payload fixtures for easy iteration in tests.
    """
    return [
        question_payload_minimal_dict,
        question_payload_full_dict,
        question_payload_mechanics,
        question_payload_thermo,
        question_payload_fluids,
    ]





@pytest.fixture
def invalid_question_payloads():
    # Values that should NOT work
    return [
        "question_data",
        ["A list of values of question data"],
        123,
        None,
    ]


# Helpers
def create_question(client, payload, metadata=None, files=None):
    data = {"question": json.dumps(payload)}
    if metadata:
        data["additional_metadata"] = json.dumps(metadata)

    resp = client.post("/questions/", data=data, files=files)
    assert resp.status_code == 201, resp.text

    # Re-validate response data against the schema
    response_data = resp.json()
    validated = QuestionReadResponse.model_validate(response_data)
    assert validated

    return validated.question





def retrieve_single_file(client, qid, filename):
    resp = client.get(f"/questions/{qid}/files/{filename}")
    assert resp.status_code == 200, resp.text
    response_data = resp.json()
    validated = SuccessDataResponse.model_validate(response_data)
    return normalize_content(validated.data)


def retrieve_files(
    client, qid, route_arg: Literal["files", "files_data"]
) -> SuccessFileResponse:
    resp = client.get(f"/questions/{qid}/{route_arg}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    validated = SuccessFileResponse.model_validate(body)
    assert validated
    logger.debug(f"This is the validated retrieved {validated}")
    return validated


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------







@pytest.fixture
def create_multiple_question(test_client, all_question_payloads):
    """Ensure multiple question payloads can be created sequentially."""
    for p in all_question_payloads:
        serializable = to_serializable(p)
        data = {"question": json.dumps(serializable)}
        response = test_client.post("/questions/", data=data)
        assert response.status_code == 201
