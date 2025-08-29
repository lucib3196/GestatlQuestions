from __future__ import annotations
from uuid import UUID
from typing import Union, Optional, List
from pydantic import BaseModel
from backend_api.model.question_model import Question, QuestionMeta
from backend_api.model import File
from backend_api.data.database import SessionDep
from backend_api.service import question_crud
from backend_api.service import question_file_service
from starlette import status
from fastapi import APIRouter, HTTPException


router = APIRouter(prefix="/question_crud")


class QuestionFile(BaseModel):
    filename: str
    content: Union[str, dict]


class QuestionReadResponse(BaseModel):
    status: int
    question: QuestionMeta
    files: Optional[List[File]]
    detail: str


class AdditionalQMeta(BaseModel):
    topics: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    qtype: Optional[List[str]] = None


@router.post("/create_question/text/")
async def create_question(
    question: Union[Question, dict],
    session: SessionDep,
    files: Optional[List[QuestionFile]] = None,
    additional_metadata: Optional[AdditionalQMeta] = None,
) -> QuestionReadResponse:
    try:
        if isinstance(question, Question):
            base_question = question.model_dump()
        else:
            base_question = question

        if additional_metadata:
            base_question = {**base_question, **additional_metadata.model_dump()}

        q_created = await question_crud.create_question(
            base_question,
            session,
        )
        if files:
            for f in files:
                question_file_service.add_file_to_question(
                    question_id=q_created.id,
                    filename=f.filename,
                    content=f.content,
                    session=session,
                )
        return QuestionReadResponse(
            status=status.HTTP_201_CREATED,
            question=QuestionMeta.model_validate(q_created),
            files=q_created.files,
            detail=f"Created question {q_created.title}",
        )
    except HTTPException:
        raise


@router.get("/get_question_data_meta/{qid}")
async def get_question_only_data_meta_by_id(
    qid: Union[str, UUID], session: SessionDep
) -> QuestionReadResponse:
    q_response = QuestionMeta.model_validate(
        await question_crud.get_question_data(qid, session)
    )
    return QuestionReadResponse(
        status=status.HTTP_200_OK,
        question=q_response,
        files=None,
        detail=f"Retrieved question data {q_response.title}",
    )


@router.get("/get_question_data_all/{qid}")
async def get_question_data_all_by_id(
    qid: Union[str, UUID], session: SessionDep
) -> QuestionReadResponse:
    try:
        q = await question_crud.get_question_data(qid, session)
        q_response = QuestionMeta.model_validate(q)
        file_response = question_file_service.get_all_files(q_response.id, session)
        return QuestionReadResponse(
            status=status.HTTP_200_OK,
            question=q_response,
            files=file_response.file_obj,
            detail=f"Retrieved question data {q_response.title}",
        )
    except HTTPException:
        raise
