from backend_api.model.questions_models import QuestionMetaNew
from backend_api.model.questions_models import Question, File, QuestionDict
from backend_api.data.database import SessionDep
import json
from typing import Union, List
from sqlmodel import select
from backend_api.core.logging import logger
from typing import TypedDict
from uuid import UUID
from fastapi import HTTPException
from starlette import status
from sqlalchemy.exc import SQLAlchemyError
from json import JSONDecodeError
from pydantic import ValidationError


# Utils
def get_question_id_UUID(question_id) -> UUID:
    try:
        question_uuid = UUID(question_id)
        return question_uuid
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


# Most Generic
async def add_question(question: Question, session: SessionDep):
    session.add(question)
    session.commit()
    session.refresh(question)
    return question


async def add_file(file_obj: File, session: SessionDep):
    if isinstance(file_obj.content, dict):
        file_obj.content = json.dumps(file_obj.content)
    session.add(file_obj)
    session.commit()
    session.refresh(file_obj)
    return file_obj


# Getting Methods
async def get_question_qmeta(question_id: str, session: SessionDep):
    question_uuid = get_question_id_UUID(question_id)
    result = session.exec(
        select(File)
        .where(File.question_id == question_uuid)
        .where(File.filename == "qmeta.json")
    ).first()

    # Checking to see if there is any content
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question has no qmeta"
        )
    if result.content is None or (
        isinstance(result.content, str) and not result.content.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="qmeta.json exists but has no content.",
        )

    try:
        raw: Union[dict, list]
        if isinstance(result.content, (dict, list)):
            raw = result.content
        elif isinstance(result.content, str):
            raw = json.loads(result.content)
        else:
            # Unexpected type (e.g., bytes)
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported content type for qmeta.json: {type(result.content).__name__}",
            )
    except JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON in qmeta.json: {e.msg} at pos {e.pos}",
        )
    try:
        qmeta = QuestionMetaNew(**raw)  # type: ignore
    except ValidationError as e:
        # Return Pydantic errors cleanly
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "qmeta failed validation", "errors": e.errors()},
        )

    return qmeta


async def add_question_and_files(
    question: Question, files: dict[str, Union[str, dict]], session: SessionDep
) -> Question:
    question = await add_question(question, session)
    for filename, contents in files.items():
        if isinstance(contents, (dict, list)):
            contents = json.dumps(contents)

            file_obj = File(
                filename=filename, content=contents, question_id=question.id
            )

            await add_file(file_obj, session)
    return question


async def get_all_questions(
    session: SessionDep,
    offset: int = 0,
    limit: int = 100,
):
    results = session.exec(select(Question).offset(offset).limit(limit)).all()
    return results


async def filter_questions(session: SessionDep, qfilter: QuestionDict):
    filters = []
    for key, value in qfilter.items():
        logger.debug("Filter: %s = %r", key, value)

        col = getattr(Question, key, None)
        if col:
            if key == "title":
                logger.debug("Adjusting Title Search")
                filters.append(Question.title.ilike(f"%{value}%"))  # type: ignore
            else:
                filters.append(col == value)
    logger.info("Current Filters %s", filters)
    result = session.exec(select(Question).where(*filters)).all()
    logger.info("Results %s", result)
    return result


async def delete_question(question_id: UUID, session: SessionDep):
    result = session.exec(select(Question).where(Question.id == question_id)).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )
    title = result.title
    try:
        session.delete(result)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Could not delete question") from e

    return {"detail": f"Question '{title}' deleted", "id": str(question_id)}


async def update_file(
    question_id: str,
    filename: str,
    newcontent: Union[str, dict, list],
    session: SessionDep,
):
    """Update a file's content for a given question. Returns the updated row."""
    if not filename or not filename.strip():
        raise HTTPException(status_code=400, detail="Filename is required")
    question_uuid = get_question_id_UUID(question_id)

    # Fetch the content
    file_obj = session.exec(
        select(File).where(
            (File.question_id == question_uuid) & (File.filename == filename.strip())
        )
    ).first()

    if file_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not present in question",
        )

    if isinstance(newcontent, (dict, list)):
        newcontent = json.dumps(newcontent, ensure_ascii=False)

    # Make changes
    file_obj.content = newcontent
    # Commit & refresh the *object*, not the value
    try:
        session.commit()
        session.refresh(file_obj)
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update file") from exc

    return {
        "detail": "updated",
        "filename": file_obj.filename,
        "new_content": newcontent,
        "question_id": str(file_obj.question_id),
    }
