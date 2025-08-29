import pytest
from backend_api.model.question_model import Question
from ai_workspace.utils import to_serializable
from fastapi.encoders import jsonable_encoder


@pytest.fixture
def question_payload_model_no_files():
    q = Question(
        title="Sample Question",
        ai_generated=True,
        isAdaptive=False,
        createdBy="tester",
        user_id=1,
    )
    payload = {"question": to_serializable(q)}
    return payload


@pytest.fixture
def question_payload_model_with_files():
    q = Question(
        title="QuestionWithFiles",
        ai_generated=True,
        isAdaptive=False,
        createdBy="tester",
        user_id=1,
    )
    files_data = [
        ("question.html", "Some question text"),
        ("solution.html", "Some solution"),
        ("server.js", "some code content"),
        ("meta.json", {"content": "some content"}),
    ]
    files_payload = {
        "files": [
            {"filename": fname, "content": content} for fname, content in files_data
        ]
    }

    print("this is the files payload", files_payload)

    payload = {"question": to_serializable(q), **files_payload}
    return payload


@pytest.fixture
def question_payload_with_files_and_meta():
    q = Question(
        title="QuestionWithFiles",
        ai_generated=True,
        isAdaptive=False,
        createdBy="tester",
        user_id=1,
    )

    files_data = [
        ("question.html", "Some question text"),
        ("solution.html", "Some solution"),
        ("server.js", "some code content"),
        ("meta.json", {"content": "some content"}),
    ]
    files_payload = {
        "files": [
            {"filename": fname, "content": content} for fname, content in files_data
        ]
    }

    additional_metadata = {
        "topics": ["Mechanics", "Statics"],
        "languages": ["python", "javascript"],
        "qtype": ["numeric"],
    }

    print("this is the files payload", files_payload)
    print("this is the additional metadata", additional_metadata)

    payload = {
        "question": to_serializable(q),
        **files_payload,
        "additional_metadata": additional_metadata,
    }
    return payload


@pytest.fixture
def create_question_response_no_files(test_client, question_payload_model_no_files):
    """Helper fixture to create a question and return the response + payload."""
    response = test_client.post(
        "/question_crud/create_question/text/",
        json=jsonable_encoder(question_payload_model_no_files),
    )
    return response, question_payload_model_no_files["question"]


@pytest.fixture
def create_question_response_with_files(test_client, question_payload_model_with_files):
    """Helper fixture to create a question and return the response + payload."""
    response = test_client.post(
        "/question_crud/create_question/text/",
        json=jsonable_encoder(question_payload_model_with_files),
    )
    return (
        response,
        question_payload_model_with_files["question"],
        question_payload_model_with_files["files"],
    )


@pytest.fixture
def create_question_response_with_additional_meta(
    test_client, question_payload_with_files_and_meta
):
    """Helper fixture to create a question and return the response + payload."""
    response = test_client.post(
        "/question_crud/create_question/text/",
        json=jsonable_encoder(question_payload_with_files_and_meta),
    )
    return (
        response,
        question_payload_with_files_and_meta["question"],
        question_payload_with_files_and_meta["files"],
        question_payload_with_files_and_meta["additional_metadata"],
    )
