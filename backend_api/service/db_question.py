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
