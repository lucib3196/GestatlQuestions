from pathlib import Path
import pytest
import json
from src.api.service import code_generation as cd
from src.api.core.logging import logger
from src.api.models import QuestionData


@pytest.fixture()
def load_mock_data():
    data = Path(r"app_test\test_assets\ai_output\gestalt_output.json")
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
