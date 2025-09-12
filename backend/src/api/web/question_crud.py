from __future__ import annotations

# --- Standard Library ---
from typing import List, Literal, Optional, Union
from uuid import UUID

# --- Third-Party ---
from fastapi import APIRouter, HTTPException
from starlette import status

# --- Internal ---
from src.api.database import SessionDep
from src.api.models.question_model import Question, QuestionMeta
from src.api.response_models import *
from src.api.service import question_crud
from src.api.service import question_storage_service as qs
from src.utils import normalize_kwargs


router = APIRouter(prefix="/question_crud", tags=["question_crud"])


@router.post("/create_question/text/")
async def create_question(
    question: Union[Question, dict],
    session: SessionDep,
    files: Optional[List[FileData]] = None,
    additional_metadata: Optional[AdditionalQMeta] = None,
    save_dir: Literal["local", "firebase"] = "local",
) -> QuestionReadResponse:
    """
    Create a new question and optionally attach files.

    Args:
        question (Union[Question, dict]): The question payload (model or dict).
        session (SessionDep): Database session dependency.
        files (Optional[List[FileData]]): Files to associate with the question.
        additional_metadata (Optional[AdditionalQMeta]): Extra metadata to merge.
        save_dir (Literal["local", "firebase"]): Storage backend for files.

    Returns:
        QuestionReadResponse: Created question details and file metadata.
    """
    try:
        if isinstance(question, Question):
            base_question = question.model_dump()
        else:
            base_question = question

        if additional_metadata:
            base_question = {**base_question, **additional_metadata.model_dump()}

        q_created = await question_crud.create_question(base_question, session)

        if save_dir == "local":
            await qs.set_directory(q_created.id, session)
        elif save_dir == "firebase":
            raise NotImplementedError("Have not implemented firebase functionality")

        fresponse = []
        if files:
            response = await qs.write_files_to_directory(
                question_id=q_created.id, files_data=files, session=session
            )
            fresponse = response.filedata

        return QuestionReadResponse(
            status=status.HTTP_201_CREATED,
            question=QuestionMeta.model_validate(q_created),
            files=fresponse,
            detail=f"Created question {q_created.title}",
        )
    except HTTPException:
        raise


@router.get("/{quid}/local/")
async def get_local_dir(quid: str | UUID, session: SessionDep):
    """
    Retrieve the local directory path for a question.

    Args:
        quid (str | UUID): Question ID.
        session (SessionDep): Database session dependency.
    """
    try:
        return await qs.get_question_directory(session, quid)
    except HTTPException:
        raise


@router.get("/get_question/{qid}/file/{filename}")
async def get_question_file(qid: Union[str, UUID], filename: str, session: SessionDep):
    """
    Retrieve the contents of a specific file associated with a question.

    Args:
        qid (str | UUID): Question ID.
        filename (str): File name.
        session (SessionDep): Database session dependency.
    """
    try:
        result = await qs.get_file_content(
            question_id=qid, filename=filename, session=session
        )
        return result.filedata[0].content
    except HTTPException as e:
        raise e


@router.get("/get_question/{quid}/get_all_files")
async def get_all_question_files(quid: Union[str, UUID], session: SessionDep):
    """
    Retrieve all files associated with a question.

    Args:
        quid (str | UUID): Question ID.
        session (SessionDep): Database session dependency.
    """
    try:
        result = await qs.get_files_from_directory(question_id=quid, session=session)
        return result
    except HTTPException as e:
        raise e


@router.post("/update_file_content", status_code=200)
async def update_file(payload: UpdateFile, session: SessionDep):
    """
    Update the content of a file associated with a question.

    Args:
        payload (UpdateFile): Contains question_id, filename, and new content.
        session (SessionDep): Database session dependency.

    Returns:
        dict: Result of the update with a success flag.
    """
    try:
        result = await qs.update_file_content(
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
    """
    Retrieve only the metadata for a question (no files).

    Args:
        qid (str | UUID): Question ID.
        session (SessionDep): Database session dependency.
    """
    q_response = QuestionMeta.model_validate(
        await question_crud.get_question_data(qid, session)
    )
    return QuestionReadResponse(
        status=status.HTTP_200_OK,
        question=q_response,
        files=[],
        detail=f"Retrieved question data {q_response.title}",
    )


@router.get("/get_question_data_all/{qid}")
async def get_question_data_all_by_id(
    qid: Union[str, UUID], session: SessionDep
) -> QuestionReadResponse:
    """
    Retrieve metadata and all associated files for a question.

    Args:
        qid (str | UUID): Question ID.
        session (SessionDep): Database session dependency.
    """
    try:
        q = await question_crud.get_question_data(qid, session)
        q_response = QuestionMeta.model_validate(q)

        file_data = []
        if q_response.id is not None:
            file_response = await qs.get_files_from_directory(q_response.id, session)
            file_data = file_response.filedata

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
    """
    Retrieve all questions (basic version).

    Args:
        session (SessionDep): Database session dependency.
    """
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
    """
    Retrieve all questions with metadata, paginated.

    Args:
        session (SessionDep): Database session dependency.
        limit (int): Number of results to return. Defaults to 100.
        offset (int): Offset for pagination. Defaults to 0.
    """
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
    """
    Update metadata of a question.

    Args:
        quid (str | UUID): Question ID.
        session (SessionDep): Database session dependency.
        updates (QuestionMeta): Metadata fields to update.
    """
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
    """
    Filter questions based on metadata.

    Args:
        session (SessionDep): Database session dependency.
        filters (QuestionMeta): Filter criteria.
    """
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
    """
    Delete a question by ID.

    Args:
        quid (str | UUID): Question ID.
        session (SessionDep): Database session dependency.
    """
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
    """
    Delete all questions in the database.

    Args:
        session (SessionDep): Database session dependency.
    """
    try:
        r = await question_crud.delete_all_questions(session)
        return r
    except HTTPException as e:
        raise e
