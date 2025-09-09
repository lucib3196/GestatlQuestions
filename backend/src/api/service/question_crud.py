# Standard library
from typing import Union
from uuid import UUID
import asyncio

# Third-party
from fastapi import HTTPException
from starlette import status
from typing import Sequence, Dict, List, Any

# Local
from api.data.database import SessionDep
from api.models.question_model import (
    Question,
)
from api.data import question_db as qdata
from api.core.logging import logger
from api.utils import get_uuid


async def create_question(
    question: Union[Question, dict], session: SessionDep
) -> Question:
    if not question or (
        not isinstance(question, dict) and not isinstance(question, Question)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Question must either be object of type Question or dict or not Empty got type {type(question)}",
        )
    try:
        return qdata.create_question(question, session, True)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Processing Question Content {e}",
        )


async def get_all_questions(
    session: SessionDep,
    offset: int = 0,
    limit: int = 100,
) -> Sequence[Question]:
    results = qdata.get_all_questions(session, offset=offset, limit=limit)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, detail="No Questions in DB"
        )
    else:
        return results


async def get_question_by_id(question_id: Union[str, UUID], session: SessionDep):
    try:
        results = qdata.get_question_by_id(question_id, session)
        logger.debug("This is the result of getting the id %s", results)
        if results is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,  # 404 is more REST-correct
                detail="Question does not exist",
            )
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bad Request {str(e)}"
        )


async def delete_all_questions(session: SessionDep) -> None:
    return qdata.delete_all_questions(session)


async def delete_question_by_id(
    question_id: Union[str, UUID], session: SessionDep
) -> dict[str, str]:
    try:
        question = await get_question_by_id(question_id, session)
        qdata.delete_question_by_id(question.id, session)
        return {"detail": f"Question Deleted {question.title}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown Error {str(e)}",
        )


async def edit_question_meta(
    question_id: Union[str, UUID], session: SessionDep, **kwargs
):
    try:
        question_id = get_uuid(question_id)
        updated_question = qdata.update_question(session, question_id, **kwargs)
        return await get_question_data(question_id=updated_question.id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating Question {question_id}: {str(e)}",
        )


async def filter_questions_meta(session: SessionDep, **kwargs) -> List[Dict[str, Any]]:
    try:
        questions = qdata.filter_questions(session, **kwargs)
        tasks = [
            qdata.get_question_data(question_id=r.id, session=session)
            for r in questions
        ]
        return await asyncio.gather(*tasks)
    except HTTPException as e:
        raise e


async def get_question_data(question_id: Union[str, UUID], session: SessionDep):
    try:
        result = await qdata.get_question_data(question_id, session)
        return result
    except HTTPException as e:
        raise e


async def get_all_question_data(session: SessionDep, limit: int = 100, offset: int = 0):
    try:
        result = await qdata.get_all_question_data(session, limit=limit, offset=offset)
        return result
    except HTTPException as e:
        raise e
