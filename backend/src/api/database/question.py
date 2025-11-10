# --- Standard Library ---
import asyncio
from typing import Sequence, Union, Literal
from uuid import UUID

# --- Third-Party ---
from pydantic import ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import delete, select
from pathlib import Path

# --- Internal ---
from src.api.core import logger
from src.api.database import SessionDep, generic_db as gdb
from src.api.database.generic_db import filter_conditional
from src.api.models.models import Question
from src.api.models.question import QuestionMeta, QuestionData
from src.utils import convert_uuid


async def create_question(
    question: QuestionData | dict,
    session: SessionDep,
) -> Question:
    relationships = gdb.get_all_model_relationships(Question)

    try:
        if isinstance(question, dict):
            question = QuestionData.model_validate(question)
    except ValidationError as e:
        raise ValueError("Relationship data is not of type QRelationshipData")
    question = question.model_dump()

    relation_values = {k: v for k, v in question.items() if k in relationships}
    base_values = {k: v for k, v in question.items() if k not in relationships}

    # Contains the basic fields for the question
    question_base = Question.model_validate(base_values)
    session.add(question_base)

    for key, value in relation_values.items():
        target_class = relationships[key]
        if isinstance(value, list):
            rel_val = [
                gdb.create_or_resolve(target_class, v, session)[0] for v in value
            ]
        elif isinstance(value, str):
            rel_val = gdb.create_or_resolve(target_class, value, session)[0]
        else:
            raise NotImplementedError(
                "Have not implmeneted method to handle non list or string values "
            )
        setattr(Question, key, rel_val)

    try:
        session.commit()
        session.refresh(question_base)
        return question_base
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"[DB] could not create question {e}")
        raise ValueError(f"[DB] failed to create question an error occured {e}")


def get_question(id: str | UUID | None, session: SessionDep) -> Question | None:
    """
    Fetch a single Question by its ID.

    Args:
        question_id: The question's identifier (UUID or string convertible to UUID).
        session: Database session dependency.

    Returns:
        The matching Question instance, or None if not found.
    """
    try:
        assert id
        question_id = convert_uuid(id)
        return session.exec(select(Question).where(Question.id == question_id)).first()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"[DB] could not create question {e}")
        raise ValueError(f"[DB] failed to retrieve question an error occured {e}")


def delete_all_questions(session: SessionDep) -> bool:
    try:
        statement = delete(Question)
        session.exec(statement)
        session.commit()
        return True
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


def delete_question(id: str | UUID | None, session: SessionDep) -> bool:
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
    id: str | UUID | None,
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
    logger.info("Getting relationship data %s", relationship_data)
    question_data = question.model_dump()
    q = QuestionMeta(**question_data, **relationship_data)
    logger.info("Getting data complete %s", q)
    return q


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
    id: str | UUID, update_data: QuestionData, session: SessionDep
) -> QuestionMeta:
    relationships = gdb.get_all_model_relationships(Question)
    question = get_question(id, session)
    if not question:
        raise ValueError("Question is not found")
    for key, value in update_data.model_dump(exclude_unset=True).items():
        if value is None:
            continue
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

            logger.info("Updating question %s %s %s", question, key, rel_val)
            setattr(question, key, rel_val)
        else:
            setattr(question, key, value)
    try:
        logger.info("Adding question after update %s", question)
        session.commit()
        return await get_question_data(question.id, session)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"[DB] failed to update question {e}")
        raise ValueError(f"[DB] failed to update question {e}")


async def filter_questions(
    data: QuestionData,
    session: SessionDep,
    relationship_field: str = "name",
) -> Sequence[QuestionMeta]:
    relationships = gdb.get_all_model_relationships(Question)
    filters = []
    joins = set()
    stmt = select(Question)

    for key, value in data.model_dump(exclude_none=True).items():
        if not value:
            continue

        conds = []

        # --- Handle Relationship Filters ---
        if key in relationships:
            relationship_model = relationships[key]
            joins.add(key)
            logger.info("This is join %s", joins)
            if isinstance(value, list):
                rel_conds = [
                    filter_conditional(
                        relationship_model,
                        relationship_field,
                        v,
                    )
                    for v in value
                ]
                conds.append(or_(*rel_conds))
            else:
                conds.append(
                    filter_conditional(
                        relationship_model,
                        relationship_field,
                        value,
                    )
                )

        # --- Handle Regular Column Filters ---
        else:
            if isinstance(value, list):
                conds.append(
                    or_(*[filter_conditional(Question, key, v) for v in value])
                )
            else:

                conds.append(filter_conditional(Question, key, value))

        if conds:
            filters.append(or_(*conds))

    # --- Apply Filters ---
    # --- Apply Relationship Joins ---
    if filters:
        stmt = stmt.where(*filters)

    stmt = stmt.distinct()  # prevent non uniqy

    # IDK how to fix
    # for rel in joins:
    #     logger.info("joining on rel=%s type=%s", rel, type(rel))
    #     print("Question type:", type(Question))
    #     stmt = stmt.join(getattr(Question, rel))

    # --- Execute and Return ---
    results = session.exec(stmt).all()
    return await asyncio.gather(*[get_question_data(r.id, session) for r in results])


def get_question_path(
    id: str | UUID | None, storage_type: Literal["cloud", "local"], session: SessionDep
) -> str | None:
    """Retrieve the storage path (cloud or local) for a question."""
    question = get_question(id, session)
    if not question:
        raise ValueError("Question not found")

    if storage_type == "cloud":
        return question.blob_path
    elif storage_type == "local":
        return question.local_path
    else:
        raise ValueError(f"Invalid storage type: {storage_type}")


def set_question_path(
    id: str | UUID | None,
    path: Path | str,
    storage_type: Literal["cloud", "local"],
    session: SessionDep,
) -> Question:
    """
    Update the question's storage path (local or cloud) and persist the change in the database.
    """
    question = get_question(id, session)
    if not question:
        raise ValueError("Question not found")

    path_str = Path(path).as_posix()
    try:
        if storage_type == "cloud":
            question.blob_path = path_str
        elif storage_type == "local":
            question.local_path = path_str
        else:
            raise ValueError(f"Invalid storage type: {storage_type}")

        session.add(question)
        session.commit()
        session.refresh(question)
        return question

    except SQLAlchemyError as e:
        session.rollback()
        raise RuntimeError(f"Failed to update question path: {e}")
