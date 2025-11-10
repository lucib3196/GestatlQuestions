# --- Standard Library ---
from typing import Optional

# --- Third-Party ---
from fastapi import UploadFile, HTTPException

# --- Internal ---
from src.api.core.config import get_settings
from src.api.core import logger
from src.api.models.models import Question
from src.api.models import *
from src.api.service.file_service import FileService
from src.utils import serialized_to_dict

app_settings = get_settings()


def parse_question_payload(
    question: str | dict | Question,
    additional_metadata: Optional[str | AdditionalQMeta],
):
    logger.debug(f"Received question {question} type of {type(question)}")
    question = serialized_to_dict(question, Question)
    if additional_metadata:
        question.update(serialized_to_dict(additional_metadata, AdditionalQMeta))
    return question


# async def parse_file_upload(file: UploadFile) -> FileData:
#     f = await FileService("").validate_file(file)
#     content = await f.read()
#     await f.seek(0)
#     fd = FileData(filename=str(f.filename), content=content)
#     return fd


