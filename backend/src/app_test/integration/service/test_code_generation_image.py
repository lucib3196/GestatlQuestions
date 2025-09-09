import pytest
from app_test.integration.service.fixture_code_generation import *
from api.service import code_generation
from api.service import question_crud
from fastapi import UploadFile
import io


@pytest.mark.asyncio
async def test_file_upload(db_session, simple_question_text):
    contents = open("app_test/assets/test_image.png", "rb").read()
    upload_file = UploadFile(filename="test_image.jpg", file=io.BytesIO(contents))

    result = await code_generation.run_image(
        files=[upload_file],
        session=db_session,
        meta=simple_question_text["additional_meta"],
    )
    assert result["success"] is True
    assert "questions" in result
    print(result["questions"])
