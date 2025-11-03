import json
from pathlib import Path
import pytest
from src.api.models import FileData, QuestionReadResponse


@pytest.fixture
def question_data():
    """Minimal question payload."""
    return {
        "title": "SomeTitle",
        "ai_generated": True,
        "isAdaptive": True,
        "createdBy": "John Doe",
        "user_id": 1,
    }


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


def retrieve_question(client, qid):
    resp = client.get(f"/questions/{qid}")
    assert resp.status_code == 200, resp.text
    response_data = resp.json()
    validated = QuestionReadResponse.model_validate(response_data)
    assert validated
    return validated.question


@pytest.fixture
def server_files():
    """Static assets used by question endpoints."""
    base = Path("app_test/test_assets/code")
    return [
        FileData(filename="server.js", content=(base / "generate.js").read_bytes()),
        FileData(filename="server.py", content=(base / "generate.py").read_bytes()),
    ]
