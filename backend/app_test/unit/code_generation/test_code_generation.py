# --- Standard Library ---
import io
import json
from pathlib import Path

# --- Third-Party ---
import pytest
from fastapi import UploadFile
from pydantic_settings import BaseSettings

# --- Internal ---
from src.api.service import code_generation as cd
from src.api.core.logging import logger
from src.api.models import QuestionData


class TestConfig(BaseSettings):
    asset_path: Path


test_config = TestConfig(asset_path=Path("app_test/test_assets").resolve())


@pytest.fixture
def simple_question_text():
    """Basic free-response style physics question."""
    question = (
        "A ball is traveling along a straight road at a constant speed of 20 miles per hour. "
        "What is the total distance traveled after 5 hours?"
    )
    additional_metadata = {"user_id": 0, "created_by": "Luciano@gmail.com"}
    return {"question": question, "additional_meta": additional_metadata}


@pytest.fixture
def multiple_choice_math_question():
    """Multiple-choice algebra question."""
    question = (
        "What is the solution to the equation 2x + 3 = 7?\n"
        "A) x = 1\nB) x = 2\nC) x = 3\nD) x = 4"
    )
    additional_metadata = {"user_id": 1, "created_by": "MathTeacher"}
    return {"question": question, "additional_meta": additional_metadata}


@pytest.fixture
def conceptual_physics_question():
    """Conceptual physics (no numbers, reasoning based)."""
    question = "Why does an object in motion stay in motion unless acted upon by an external force?"
    additional_metadata = {"user_id": 2, "created_by": "PhysicsDept"}
    return {"question": question, "additional_meta": additional_metadata}


@pytest.fixture
def question_payloads(
    simple_question_text,
    multiple_choice_math_question,
    conceptual_physics_question,
):
    """
    Aggregate all individual question fixtures into a single list
    so tests can iterate over them.
    """
    return [
        simple_question_text,
        multiple_choice_math_question,
        conceptual_physics_question,
    ]


@pytest.fixture()
def load_mock_data():
    data = Path(r"app_test/test_assets/ai_output/gestalt_output.json")
    return json.loads(data.read_text())


def test_validate_data(load_mock_data):
    assert cd.validate_data(load_mock_data)


def test_process_question_data(load_mock_data):
    data = cd.process_question_data(load_mock_data)
    logger.info("This is the qdata %s", data)
    assert isinstance(data, QuestionData)


def test_process_code_files(load_mock_data):
    data = cd.process_code_files(load_mock_data)
    assert isinstance(data, list)
    logger.info("This are the files %s", data)


@pytest.mark.asyncio
@pytest.mark.parametrize("payload_index", range(1))  # adjust to len(question_payloads)
async def test_run_text_each(question_payloads, payload_index):
    payload = question_payloads[payload_index]
    result = await cd.run_text(
        text=payload["question"],
    )
    assert result
    logger.info("This is the text generation result %s", result)


@pytest.mark.asyncio
async def test_file_upload():
    image_path = test_config.asset_path / "images" / "mass_block.png"
    contents = open(image_path, "rb").read()
    upload_file = UploadFile(filename="mass_block.png", file=io.BytesIO(contents))

    result = await cd.run_image(
        files=[upload_file],
    )
    assert result
