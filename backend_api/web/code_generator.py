from pydantic import BaseModel, Field
from typing import List, Union, Literal, Optional
from fastapi import APIRouter, Depends
from backend_api.service import local_questions as service
from backend_api.model.questions_models import QuestionMeta, QuestionMetaNew
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import backend_api.service.code_generator as service
from ai_workspace.agents.code_generators.v4.qmeta import (
    OutputState as CodeGenOutputState,
)
from backend_api.data.database import get_session
from backend_api.model.questions_models import Question, CodeLanguage
from backend_api.service import user

router = APIRouter(prefix="/codegenerator")
# Loads up directory and get all the questions
local_questions = Path.cwd() / "./local_questions"


class TextGenV4Input(BaseModel):
    question: List[str]
    question_title: str | None


@router.post("/v4/text_gen/")  # response_model=CodeGenOutputState)
async def generate_question_v4(
    data: TextGenV4Input,
    current_user=Depends(user.get_current_user),
    session=Depends(get_session),
):
    user_id = await user.get_user_by_name(
        username=current_user.username, email=current_user.email, session=session
    )
    
    
    
    

    question = Question(
        user_id=user_id,
        qtype=["numeric"],
        title=data.question_title or "Question",
        topic=["general"],
        isAdaptive=True,
        createdBy=current_user.email,
        language=["python"],  # type: ignore
        ai_generated=True,
    )
    session.add(question)
    session.commit()
    session.refresh(question)
    return question
