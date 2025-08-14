from __future__ import annotations

import json
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend_api.data.database import get_session
from backend_api.model.questions_models import (
    File,
    Question,
)

from backend_api.service import user
from ai_workspace.agents.code_generators.v4_5.main_text import (
    InputState,
    IntermediateState,
    app as text_gen,
)
from ai_workspace.utils import to_serializable

router = APIRouter(prefix="/codegenerator")


# Loads up directory and get all the questions
class TextGenV4Input(BaseModel):
    question: List[str]
    question_title: Optional[str]


@router.post("/v4/text_gen/")  # response_model=CodeGenOutputState)
async def generate_question_v4(
    data: TextGenV4Input,
    current_user=Depends(user.get_current_user),
    session=Depends(get_session),
):
    user_id = await user.get_user_by_name(
        username=current_user.username,
        email=current_user.email,
        session=session,
    )

    results = await text_gen.ainvoke(InputState(text=data.question[0]))
    state = IntermediateState.model_validate(results)
    raw_list = state.code_results or []
    code_results = raw_list if isinstance(raw_list, list) else [raw_list]

    questions = []
    for cr in code_results:
        question = Question(
            user_id=user_id,
            qtype=cr.qmeta.qtype,
            title=data.question_title or cr.qmeta.title,
            topic=cr.qmeta.topic,
            isAdaptive=cr.qmeta.isAdaptive,
            language=cr.qmeta.language,
            ai_generated=True,
        )

        questions.append(question)
        session.add(question)
        session.commit()
        session.refresh(question)

        for filename, content in cr.files.model_dump().items():
            if isinstance(content, dict):
                content = json.dumps(content)
            file_obj = File(
                filename=filename,
                content=content,
                question_id=question.id,
            )
            session.add(file_obj)
            session.commit()
            session.refresh(file_obj)

        qmeta_file = File(
            filename="qmeta.json",
            content=to_serializable(cr.qmeta),
            question_id=question.id,
        )
        session.add(qmeta_file)
        session.commit()
        session.refresh(qmeta_file)

    return questions
