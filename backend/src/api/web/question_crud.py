from __future__ import annotations
from uuid import UUID
from typing import Union, Optional, List
from pydantic import BaseModel
from api.models.question_model import Question, QuestionMeta
from api.models import File
from api.data.database import SessionDep
from api.service import question_crud
from api.service import question_file_service
from starlette import status
from fastapi import APIRouter, HTTPException
from api.core.logging import logger
from api.utils import normalize_kwargs
from fastapi import Body

router = APIRouter(prefix="/question_crud")


class QuestionFile(BaseModel):
    filename: str
    content: Union[str, dict]


class Response(BaseModel):
    status: int
    detail: str


class QuestionReadResponse(BaseModel):
    status: int
    question: QuestionMeta
    files: Optional[List[File]]
    detail: str


class UpdateFile(BaseModel):
    question_id: str | UUID
    filename: str
    new_content: str | dict


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


@router.get("/get_question/{qid}/file/{filename}")
async def get_question_file(qid: Union[str, UUID], filename: str, session: SessionDep):
    try:
        result = question_file_service.get_question_file(
            question_id=qid, filename=filename, session=session
        )
        print(result)
        return result.file_obj[0]
    except HTTPException as e:
        raise e


@router.get("/get_question/{quid}/get_all_files")
async def get_all_question_files(quid: Union[str, UUID], session: SessionDep):
    try:
        result = question_file_service.get_all_files(question_id=quid, session=session)
        return result.file_obj
    except HTTPException as e:
        raise e


@router.post("/update_file_content", status_code=200)
async def update_file(
    payload: UpdateFile,
    session: SessionDep,
):
    """
    Update the content of a file associated with a question.

    Args:
        payload (UpdateFile): Encapsulates (question_id, filename, new_content).
        session (SessionDep): Database session dependency.

    Returns:
        dict: { success: bool, result: ... } if successful.
    """
    try:
        result = question_file_service.update_question_file(
            question_id=payload.question_id,
            filename=payload.filename,
            new_content=payload.new_content,
            session=session,
        )
        return {"success": True, "result": result}
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
        file_data = []
        if q_response.id is not None:
            file_response = question_file_service.get_all_files(q_response.id, session)
            file_data = file_response.file_obj
        return QuestionReadResponse(
            status=status.HTTP_200_OK,
            question=q_response,
            files=file_data,
            detail=f"Retrieved question data {q_response.title}",
        )
    except HTTPException:
        raise


@router.get("/get_all_questions_simple/{limit}/{offset}")
async def get_all_questions_data(session: SessionDep):
    try:
        q = await question_crud.get_all_questions(session)
        return q
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={e}
        )


@router.get("/get_all_questions_meta/{limit}/{offset}")
async def get_all_questions_meta(
    session: SessionDep, limit: int = 100, offset: int = 0
):
    try:
        q = await question_crud.get_all_question_data(
            session=session, limit=limit, offset=offset
        )
        return q
    except HTTPException as e:
        raise e


@router.patch("/update_question/{quid}")
async def update_question(
    quid: Union[str, UUID], session: SessionDep, updates: QuestionMeta
):
    try:
        kwargs = updates.model_dump(exclude_none=True)
        norm_k = normalize_kwargs(kwargs)
        result = await question_crud.edit_question_meta(
            question_id=quid, session=session, **norm_k
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/filter_questions/")
async def filter_questions(session: SessionDep, filters: QuestionMeta):
    try:
        kwargs = filters.model_dump(exclude_none=True)
        norm_k = normalize_kwargs(kwargs)
        result = await question_crud.filter_questions_meta(session, **norm_k)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/delete_question/{quid}")
async def delete_question_by_id(
    quid: Union[str, UUID], session: SessionDep
) -> Response:
    try:
        r = await question_crud.delete_question_by_id(quid, session)
        return Response(detail=r["detail"], status=status.HTTP_200_OK)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/delete_all_questions")
async def delete_all(session: SessionDep):
    try:
        r = await question_crud.delete_all_questions(session)
    except HTTPException as e:
        raise e
