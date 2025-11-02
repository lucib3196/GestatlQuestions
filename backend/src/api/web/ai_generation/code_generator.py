from __future__ import annotations

# --- Standard Library ---
from typing import Optional, List

# --- Third-Party ---
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

# --- Internal ---
from src.api.service.code_generation import run_text, run_image
from fastapi import UploadFile
from src.api.service.question_manager import QuestionManagerDependency

router = APIRouter(prefix="/codegenerator", tags=["code_generator"])


# Loads up directory and get all the questions
class TextGenInput(BaseModel):
    question_title: Optional[str] = None
    question: str


@router.post("/v5/text_gen")
async def generate_question_v5(
    qm: QuestionManagerDependency,
    data: TextGenInput = Body(..., embed=True),
):

    additional_meta = {
        # "createdBy": current_user.email,
        # "user_id": user_id,
        "title": data.question_title
        or None,
    }
    try:
        return await run_text(
            text=data.question,
        )
    except HTTPException as e:
        raise e


@router.post("/v5/image_gen")
async def generate_question_image_v5(
    files: List[UploadFile],
):
    try:
        return await run_image(
            files,
        )
    except HTTPException as e:
        raise e
