# Stdlib
from typing import Dict, List, Sequence, Union, Any
from uuid import UUID
import asyncio

# Third-party
from sqlalchemy import or_
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import delete
from pydantic import ValidationError

# Internal
from src.api.database import SessionDep
from src.api.models.models import Question
from src.api.models.question import QuestionMeta, QuestionUpdate
from src.utils import *
from src.api.core.logging import logger
from src.api.database.generic_db import create_or_resolve
from src.api.core import logger
from src.utils import convert_uuid
from src.api.database.question_relationship_db import (
    create_language,
    create_qtopic,
    create_qtype,
)
from src.api.models.question import QRelationshipData
from src.api.database import generic_db as gdb


def create_question(
    question: Question,
    session: SessionDep,
    relationship_data: Optional[QRelationshipData | dict] = None,
):
    try:
        session.add(question)
        if relationship_data:
            if isinstance(relationship_data, dict):
                try:
                    relationship_data = QRelationshipData.model_validate(
                        relationship_data
                    )
                except ValidationError as e:
                    raise ValueError(
                        "Relationship data is not of type QRelationshipData"
                    )
            question.topics = [
                create_qtopic(t, session) for t in relationship_data.topics
            ]
            question.languages = [
                create_language(t, session) for t in relationship_data.languages
            ]
            question.qtypes = [
                create_qtype(t, session) for t in relationship_data.qtypes
            ]

        session.commit()
        session.refresh(question)
        return question
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"[DB] could not create question {e}")
        raise ValueError(f"[DB] failed to create question an error occured {e}")


def get_question(id: str | UUID, session: SessionDep) -> Question | None:
    """
    Fetch a single Question by its ID.

    Args:
        question_id: The question's identifier (UUID or string convertible to UUID).
        session: Database session dependency.

    Returns:
        The matching Question instance, or None if not found.
    """
    try:
        question_id = convert_uuid(id)
        return session.exec(select(Question).where(Question.id == question_id)).first()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"[DB] could not create question {e}")
        raise ValueError(f"[DB] failed to retrieve question an error occured {e}")


def delete_all_questions(session: SessionDep):
    try:
        statement = delete(Question)
        session.exec(statement)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"[DB] failed to delete all questions {e}")
        raise ValueError(f"[DB] failed todelete all questions an error occured {e}")


def get_all_questions(
    session: SessionDep,
    offset: int = 0,
    limit: int = 100,
) -> Sequence[Question]:
    """
    Retrieve a paginated list of Question rows.

    Args:
        session: Database session dependency.
        offset: Number of rows to skip (default 0).
        limit: Maximum number of rows to return (default 100).

    Returns:
        A sequence of Question instances.
    """
    try:
        return session.exec(select(Question).offset(offset).limit(limit)).all()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"[DB] failed to retrieve all questions {e}")
        raise ValueError(f"[DB] failed to retrieve all question {e}")


def delete_question(id: str | UUID, session: SessionDep) -> bool:
    try:
        question = get_question(id, session)
        if not question:
            logger.warning("[DB] cannot delete question, question is not found")
            return False
        session.delete(question)
        session.commit()
        session.flush()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"[DB] failed to delete question {e}")
        raise ValueError(f"[DB] failed to delete question {e}")


async def get_question_data(
    id: Union[str, UUID],
    session: SessionDep,
) -> QuestionMeta:
    """
    Retrieve a Question as a dict and include specified relationship data.

    Args:
        question_id: The question's identifier (UUID or string convertible to UUID).
        session: Database session dependency.
        rels: Relationship names to include in the response (default: topics, qtypes, languages).

    Returns:
        A dict representing the Question plus relationship values.

    Raises:
        HTTPException(404): If the question is not found.
    """
    question = get_question(id, session)
    if not question:
        logger.info("Question is none")
        raise ValueError("Could not get question data question is None")
    relationship_data = gdb.get_all_model_relationship_data(question, Question)
    question_data = question.model_dump()
    return QuestionMeta(**question_data, **relationship_data)


async def get_all_question_data(
    session: SessionDep, offset: int = 0, limit: int = 100
) -> Sequence[QuestionMeta]:
    """
    Retrieve paginated Questions and return each as a dict with relationships.

    Args:
        session: Database session dependency.
        offset: Number of rows to skip (default 0).
        limit: Maximum number of rows to return (default 100).

    Returns:
        A list of dicts, each representing a Question with relationship values.
    """
    results: Sequence[Question] = get_all_questions(session, offset=offset, limit=limit)
    logger.debug("These are the questions %s", results)
    tasks = [get_question_data(r.id, session=session) for r in results]
    return await asyncio.gather(*tasks)


async def update_question(
    id: str | UUID, update_data: QuestionUpdate, session: SessionDep
) -> QuestionMeta:
    relationships = gdb.get_all_model_relationships(Question)
    question = get_question(id, session)
    if not question:
        raise ValueError("Question is not found")
    for key, value in update_data.model_dump(exclude_unset=True).items():
        if key in relationships:
            target_class = relationships[key]
            if isinstance(value, list):
                rel_val = [
                    gdb.create_or_resolve(target_class, v, session)[0] for v in value
                ]

            elif isinstance(value, str):
                rel_val = gdb.create_or_resolve(target_class, value, session)[0]

            else:
                raise ValueError(
                    f"Got value of type {type(value)} not expected and not implemented yet"
                )
            setattr(question, key, rel_val)
        else:
            setattr(question, key, value)
    try:
        session.add(question)
        session.commit()
        session.refresh(question)
        return await get_question_data(question.id, session)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"[DB] failed to update question {e}")
        raise ValueError(f"[DB] failed to update question {e}")


# # Todo make this a bit more general and handle
def filter_questions(
    session,
    filters=None,
    partial_match=True,
    **kwargs,
):
    """
    Filter Question rows by scalar columns and/or related labels.

    Args:
        session: Database session.
        partial_match: If True, string filters use a partial/LIKE-style match; otherwise exact.
        **kwargs: Field -> value(s) mapping. For relationships, pass strings or related instances.

    Returns:
        A list of Question instances matching the combined filters (AND across fields, OR within values).
    """
    mapper = sa_inspect(Question)
    if not filters:
        filters = []

    # Deconstruct the mapping
    for key, value in kwargs.items():
        # skip unknown attributes
        try:
            prop = mapper.get_property(key)
        except Exception:
            continue

        values = value if isinstance(value, (list, tuple, set)) else [value]
        values = normalize_values(values)
        if not values:
            continue

        attr = getattr(Question, key)

        # Handles relationships
        if isinstance(prop, RelationshipProperty):
            target_cls = prop.mapper.class_
            label_col = pick_related_label_col(target_cls)
            conds = []
            for v in values:
                if isinstance(v, str):
                    inner = string_condition(label_col, v, partial=partial_match)
                else:
                    inner = label_col == v

                if prop.uselist:  # many-to-many / one-to-many
                    conds.append(attr.any(inner))
                else:  # many-to-one / one-to-one
                    conds.append(attr.has(inner))

            filters.append(or_(*conds))
            continue

        if isinstance(prop, ColumnProperty):
            col = attr
            conds = []
            for v in values:
                if isinstance(v, str):
                    conds.append(string_condition(col, v, partial=partial_match))
                else:
                    conds.append(col == v)
            filters.append(or_(*conds))
            continue
    stmt = select(Question)
    if filters:
        stmt = stmt.where(*filters)  # AND across keys, OR within each key
    return session.exec(stmt).all()
