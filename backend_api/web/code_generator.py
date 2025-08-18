from __future__ import annotations

# Stdlib
import asyncio
import json
import os
import shutil
import tempfile
from typing import List, Optional

# Third-party
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File as FileParam,  # <-- FastAPI's file parameter helper
)
from starlette import status
from pydantic import BaseModel

# Internal
from backend_api.data.database import get_session
from backend_api.model.questions_models import (
    File as FileModel,  # <-- Your SQLModel table
    Question,
)
from backend_api.core.logging import logger
from backend_api.service import generated_code_repository
from backend_api.utils.utils import to_bool
from ai_workspace.agents.code_generators.v4_5.main_text import (
    InputState,
    IntermediateState,
    app as text_gen,
)
from ai_workspace.agents.code_generators.v4_5.main_image import (
    InputState as ImageInputState,
    IntermediateState as ImageOutputState,
    app as image_gen,
)
from ai_workspace.utils import to_serializable
from backend_api.service import user

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
    if not user_id:
        return HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Must be logged in to use generation",
        )

    results = await text_gen.ainvoke(InputState(text=data.question[0]))
    state = IntermediateState.model_validate(results)
    raw_list = state.code_results or []
    code_results = raw_list if isinstance(raw_list, list) else [raw_list]
    tasks = [
        generated_code_repository.add_generated_db(
            cr, user_id=user_id, title=data.question_title, session=session
        )
        for cr in code_results
    ]
    questions = await asyncio.gather(*tasks)
    return questions


@router.post("/v4/image_gen/")
async def generate_question_image_v4(
    files: List[UploadFile],
    session=Depends(get_session),
    current_user=Depends(user.get_current_user),
):
    logger.debug("This is the current user",current_user)
    # Validate user data
    user_id = await user.get_user_by_name(
        username=current_user.username,
        email=current_user.email,
        session=session,
    )
    

    if not user_id:
        return HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Must be logged in to use generation",
        )

    temp_filepaths = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for f in files:
            temp_path = os.path.join(tmpdir, str(f.filename))
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            temp_filepaths.append(temp_path)
        results = await image_gen.ainvoke(ImageInputState(image_paths=temp_filepaths))  # type: ignore
        state = ImageOutputState.model_validate(results)
        raw_list = state.code_results or []
        code_results = raw_list if isinstance(raw_list, list) else [raw_list]
        tasks = [
            generated_code_repository.add_generated_db(
                cr, user_id=user_id, title="", session=session
            )
            for cr in code_results
        ]
        questions = await asyncio.gather(*tasks)
    return questions
