# --- Standard Library ---
import asyncio
from typing import List, Optional, Sequence, Union
from uuid import UUID

# --- Third-Party ---
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import ValidationError
from starlette import status

# --- Internal ---
from src.api.core import logger
from src.api.database import SessionDep
from src.api.dependencies import QuestionManagerDependency
from src.api.models import Question
from src.api.models.question_model import QuestionMeta
from src.api.response_models import *
from src.api.service import file_management as fm
from src.utils import normalize_kwargs, serialized_to_dict


router = APIRouter(prefix="/questions", tags=["Questions"])


def parse_question_payload(
    question: str | dict | Question,
    additional_metadata: Optional[str | AdditionalQMeta],
):
    logger.debug(f"Received question {question} type of {type(question)}")
    question = serialized_to_dict(question, Question)
    if additional_metadata:
        question.update(serialized_to_dict(additional_metadata, AdditionalQMeta))
    return question


async def parse_file_upload(file: UploadFile) -> FileData:
    f = await fm.validate_file(file)
    content = await f.read()
    await f.seek(0)
    fd = FileData(filename=str(f.filename), content=content)
    return fd


# Create
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_question(
    session: SessionDep,
    qm: QuestionManagerDependency,
    question: str = Form(...),
    additional_metadata: Optional[str] = Form(None),
    files: Optional[list[UploadFile]] = File(None),
    existing: bool = False,
):
    """
    Create a new question and set up its storage.
    """
    try:
        # Create and persist question
        qdata = parse_question_payload(question, additional_metadata)
        q = await qm.create_question(qdata, session, existing)

        logger.info("Created Question Succesfully")

        # Validate the created question model
        try:
            q = QuestionMeta.model_validate(q)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not validate the created question: {e}",
            )
        # Get all the files uploaded
        logger.info(f"Attempting to validate files: Length {len(files or [])}")

        fd_list = (
            await asyncio.gather(*[parse_file_upload(f) for f in files])
            if files
            else []
        )

        assert q.id
        await qm.save_files_to_question(q.id, session, files=fd_list)

        return QuestionReadResponse(
            status=status.HTTP_201_CREATED,
            question=q,
            files=fd_list,
            detail=f"Created question successfully {q.title}",
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log here if possible
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not create question: {e}",
        )


# Retrieval
@router.get("/{qid}", status_code=status.HTTP_200_OK)
async def get_question_metadata(
    qid: str | UUID, session: SessionDep, qm: QuestionManagerDependency
) -> QuestionReadResponse:
    try:
        question = await qm.get_question_data(qid, session)
        try:
            qmeta = QuestionMeta.model_validate(question)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not validate the created question: {e}",
            )
        return QuestionReadResponse(
            status=status.HTTP_200_OK,
            question=qmeta,
            files=[],
            detail=f"Retrieved question data {qmeta.title}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve question data: {e}",
        )


@router.get("/{qid}/full")
async def get_question_data_full(
    qid: str | UUID, session: SessionDep, qm: QuestionManagerDependency
) -> QuestionReadResponse:
    try:
        question = await qm.get_question(qid, session)
        files = await qm.read_all_files(qid, session)
        try:
            qmeta = QuestionMeta.model_validate(question)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not validate the created question: {e}",
            )

        return QuestionReadResponse(
            status=status.HTTP_200_OK,
            question=qmeta,
            files=files,
            detail=f"Retrieved question data {qmeta.title}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve question data: {e}",
        )


@router.get("/{qid}/files", status_code=status.HTTP_200_OK)
async def get_question_files(
    qid: str | UUID, session: SessionDep, qm: QuestionManagerDependency
) -> List[str]:
    try:
        return await qm.get_all_files(qid, session)
    except HTTPException:
        raise
    except Exception as e:
        # Log here if possible
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve files names: {e}",
        )


@router.get("/{qid}/files/{filename}", status_code=status.HTTP_200_OK)
async def read_question_file(
    qid: str | UUID, filename: str, session: SessionDep, qm: QuestionManagerDependency
) -> bytes | None:
    try:
        return await qm.read_file(qid, session, filename)
    except HTTPException:
        raise
    except Exception as e:
        # Log here if possible
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve files names: {e}",
        )


@router.get("/{qid}/files_data", status_code=status.HTTP_200_OK)
async def get_question_files_data(
    qid: str | UUID, session: SessionDep, qm: QuestionManagerDependency
) -> List[FileData]:
    try:
        logger.debug("Attempting to retrieve filedata")
        return await qm.read_all_files(qid, session)
    except HTTPException:
        raise
    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve files data: {e}",
        )


@router.get("/get_all/{offset}/{limit}/minimal", status_code=200)
async def get_all_questions_minimal(
    session: SessionDep,
    qm: QuestionManagerDependency,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Question]:
    try:
        results = await qm.get_all_questions(offset, limit, session)
        if results is None:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve all questions: {e}",
        )


@router.get("/get_all/{offset}/{limit}/full", status_code=200)
async def get_all_questions_full(
    session: SessionDep,
    qm: QuestionManagerDependency,
    limit: int = 100,
    offset: int = 0,
):
    try:
        results = await qm.get_all_questions_full(offset, limit, session)
        if results is None:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve all questions: {e}",
        )


# Update
@router.put("/update_file", status_code=200)
async def update_file(
    payload: UpdateFile, session: SessionDep, qm: QuestionManagerDependency
):
    try:
        new_content = FileData(filename=payload.filename, content=payload.new_content)
        result = await qm.save_file_to_question(
            payload.question_id, session, new_content, overwrite=True
        )
        return {"success": True, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        # Log here if possible
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not write file content: {e}",
        )


# TODO add test web
@router.patch("/update_question/{quid}")
async def update_question(
    quid: Union[str, UUID],
    session: SessionDep,
    updates: QuestionMeta,
    qm: QuestionManagerDependency,
):
    try:
        kwargs = updates.model_dump(exclude_none=True)
        norm_k = normalize_kwargs(kwargs)
        result = await qm.update_question(question_id=quid, session=session, **norm_k)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# Special
# TODO add test web
@router.post("/filter_questions/")
async def filter_questions(
    session: SessionDep,
    filters: QuestionMeta,
    qm: QuestionManagerDependency,
):
    """
    Filter questions based on metadata.

    Args:
        session (SessionDep): Database session dependency.
        filters (QuestionMeta): Filter criteria.
    """
    try:
        kwargs = filters.model_dump(exclude_none=True)
        norm_k = normalize_kwargs(kwargs)
        result = await qm.filter_questions(session, **norm_k)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{quid}")
async def delete_question_by_id(
    quid: Union[str, UUID],
    session: SessionDep,
    qm: QuestionManagerDependency,
) -> Response:
    """
    Delete a question by ID.

    Args:
        quid (str | UUID): Question ID.
        session (SessionDep): Database session dependency.
    """
    try:
        r = await qm.delete_question(quid, session)
        return Response(detail="Question Deleted", status=status.HTTP_200_OK)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# TODO add test web
@router.delete("/delete_all_questions", status_code=200)
async def delete_all_questions(session: SessionDep, qm: QuestionManagerDependency):
    try:
        deleted_count = await qm.delete_all_questions(session)
        return {"detail": f"Successfully deleted {deleted_count} questions"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete all questions: {str(e)}"
        )


# TODO complete this
@router.post("/{qid}/files")
async def upload_files_to_question(
    qid: str | UUID,
    files: List[UploadFile],
    session: SessionDep,
    qm: QuestionManagerDependency,
):
    try:
        fd_list = (
            await asyncio.gather(*[parse_file_upload(f) for f in files])
            if files
            else []
        )
        await qm.save_files_to_question(qid, session, fd_list, overwrite=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not upload files to question: {e}",
        )
