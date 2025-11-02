from __future__ import annotations

# Standard library
from typing import Union
from uuid import UUID
import asyncio

# Third-party
from fastapi import HTTPException
from typing import Dict, List, Any

# Local
from src.api.database import SessionDep
from src.api.database import question as qdata


async def filter_questions_meta(
    session: SessionDep, filters, **kwargs
) -> List[Dict[str, Any]]:
    """
    Filter questions by provided criteria and return full data for each match.

    Args:
        session: Database session dependency.
        **kwargs: Filter criteria supported by `question_db.filter_questions`.

    Returns:
        A list of dicts, each containing full question data.

    Raises:
        HTTPException: Propagates any HTTPExceptions from filtering or retrieval.
    """
    try:
        questions = qdata.filter_questions(session, filters, True, **kwargs)
        tasks = [
            qdata.get_question_data(question_id=r.id, session=session)
            for r in questions
        ]
        return await asyncio.gather(*tasks)
    except HTTPException as e:
        raise e


async def get_question_data(question_id: Union[str, UUID], session: SessionDep):
    """
    Retrieve a single Question's data including requested relationships.

    Args:
        question_id: Question identifier as `str` or `UUID`.
        session: Database session dependency.

    Returns:
        A dict with the question fields plus relationship arrays.

    Raises:
        HTTPException: Propagates not-found or validation errors from the DB layer.
    """
    try:
        result = await qdata.get_question_data(question_id, session)
        return result
    except HTTPException as e:
        raise e


async def get_all_question_data(session: SessionDep, limit: int = 100, offset: int = 0):
    """
    Retrieve full data for all Questions (paginated).

    Args:
        session: Database session dependency.
        limit: Maximum number of questions to fetch.
        offset: Number of questions to skip.

    Returns:
        A list of dicts, each containing full question data.

    Raises:
        HTTPException: Propagates any HTTPExceptions from the DB layer.
    """
    try:
        result = await qdata.get_all_question_data(session, limit=limit, offset=offset)
        return result
    except HTTPException as e:
        raise e
