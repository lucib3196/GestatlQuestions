from pydantic import BaseModel, Field
from typing import List, Union, Literal, Optional
from fastapi import APIRouter, Depends
from backend_api.service import local_questions as service
from backend_api.model.questions_models import QuestionMeta, QuestionMetaNew
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
import backend_api.service.code_generator as service
from ai_workspace.agents.code_generators.v4.qmeta import (
    OutputState as CodeGenOutputState,
)

router = APIRouter(prefix="/codegenerator")
# Loads up directory and get all the questions
local_questions = Path.cwd() / "./local_questions"

@router.post("/v4/text_gen", response_model=CodeGenOutputState)
async def generate_question_v4(question: str):
    raw_result = await service.generate_question_text(question)
    result = CodeGenOutputState(**raw_result)
    return result
