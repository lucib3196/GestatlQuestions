import io
from fastapi import UploadFile
import pytest
from pathlib import Path

from src.app_test.integration.fixtures.fixture_code_generation import *
from src.api.service import code_generation


@pytest.mark.asyncio
async def test_file_upload(db_session, simple_question_text):
    image_path = Path(r"backend\assets\images\mass_block.png").resolve()
    contents = open(image_path, "rb").read()
    upload_file = UploadFile(filename="test_image.jpg", file=io.BytesIO(contents))

    result = await code_generation.run_image(
        files=[upload_file],
        session=db_session,
        meta=simple_question_text["additional_meta"],
    )
    assert result["success"] is True
    assert "questions" in result
    print(result["questions"])
