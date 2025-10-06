# Stdlib
from typing import Dict, List, Sequence, Union, Any
from uuid import UUID
import asyncio

# Third-party
from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlmodel import select
from starlette import status

# Internal
from src.api.database import SessionDep
from src.api.models.question_model import Language, QType, Question, Topic
from src.utils import *
from src.api.core.logging import logger
from src.utils import resolve_or_create
from src.api.core import logger
from src.utils import convert_uuid
from datetime import datetime


def safe_refresh_question(question: Question, session: SessionDep):
    try:
        session.add(question)
        session.commit()
        session.refresh(question)
        return question
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating Question {question.id}: {e}",
        ) from e


def create_question(
    payload: Union[Question, dict],
    session: SessionDep,
) -> Question:
    """
    Create and persist a **base Question** object from either a `Question` instance
    or a `dict` payload. This only sets core fields and attaches basic relationships
    (topics, languages, qtypes). It does **not** upload files, set cloud storage
    metadata, or perform any advanced processing beyond establishing the base record.
    """
    payload = parse_question_payload(payload)

    # Define the model
    question = Question(
        title=payload["title"],
        ai_generated=payload["ai_generated"],
        isAdaptive=to_bool(payload["is_adaptive"]),
        createdBy=payload["created_by"],
        user_id=payload["user_id"],
    )

    # Handle relationships
    topic_objs = [resolve_or_create(session, Topic, t)[0] for t in payload["topics"]]
    language_objs = [
        resolve_or_create(session, Language, t)[0] for t in payload["languages"]
    ]
    qtype_objs = [resolve_or_create(session, QType, t)[0] for t in payload["qtypes"]]

    question.topics = topic_objs
    question.languages = language_objs
    question.qtypes = qtype_objs

    question = safe_refresh_question(question, session)
    return question


def get_question_by_id(question_id: str | UUID, session: SessionDep):
    """
    Fetch a single Question by its ID.

    Args:
        question_id: The question's identifier (UUID or string convertible to UUID).
        session: Database session dependency.

    Returns:
        The matching Question instance, or None if not found.
    """

    question_id = convert_uuid(question_id)
    return session.exec(select(Question).where(Question.id == question_id)).first()


def delete_all_questions(session: SessionDep):
    """
    Delete all Question rows from the database.

    Args:
        session: Database session dependency.

    Side Effects:
        Commits and flushes after deleting each row.
    """
    questions = session.exec(select(Question)).all()
    for q in questions:
        session.delete(q)
        session.commit()
        session.flush()


def delete_question_by_id(question_id: Union[str, UUID], session: SessionDep):
    """
    Delete a single Question by its ID.

    Args:
        question_id: The question's identifier (UUID or string convertible to UUID).
        session: Database session dependency.

    Returns:
        None if the question does not exist; otherwise None after deletion.

    Side Effects:
        Commits and flushes if a row was deleted.
    """
    question = get_question_by_id(question_id, session)
    if not question:
        return None
    else:
        session.delete(question)
        session.commit()
        session.flush()


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
    return session.exec(select(Question).offset(offset).limit(limit)).all()


# Utils
def parse_question_payload(
    payload: Union["Question", Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Normalize incoming payload (Question model or dict) into a consistent dict.

    Returns keys:
      - title: Optional[str]
      - ai_generated: Optional[bool]
      - is_adaptive: Optional[bool]
      - created_by: Optional[str]
      - user_id: Optional[int]
      - topics: List[Any]
      - qtypes: List[Any]
      - languages: List[Any]
    """
    try:
        # Scalars (support snake_case and camelCase)
        title = pick(payload, "title")
        ai_generated = pick(payload, "ai_generated")
        is_adaptive = pick(payload, "isAdaptive")
        created_by = pick(payload, "created_by", "createdBy")
        user_id = pick(payload, "user_id")

        # Relationships; accept multiple key variants
        t_incoming = pick(payload, "topics")
        q_incoming = pick(payload, "qtypes", "qtype")
        l_incoming = pick(payload, "languages")

        # Normalize/clean
        if isinstance(title, str):
            title = title.strip()

        return {
            "title": title,
            "ai_generated": ai_generated,
            "is_adaptive": is_adaptive,
            "created_by": created_by,
            "user_id": user_id,
            "topics": to_list(t_incoming),
            "qtypes": to_list(q_incoming),
            "languages": to_list(l_incoming),
        }
    except ValueError as e:
        raise ValueError(f"Could not parse {str(e)}")


async def get_question_data(
    question_id: Union[str, UUID],
    session: SessionDep,
    rels: List[str] = ["topics", "qtypes", "languages"],
) -> Dict[str, Any]:
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
    stmt = select(Question).where(Question.id == convert_uuid(question_id))
    result = session.exec(stmt).first()
    if result is None:
        raise ValueError("Question is None")
    data = result.model_dump()
    for r in rels:
        data[r] = get_models_relationship_data(result, r)
    return data


async def get_all_question_data(
    session: SessionDep, offset: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
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
    tasks = [get_question_data(question_id=r.id, session=session) for r in results]
    return await asyncio.gather(*tasks)


# Update
def update_question(
    session, question_id: Union[str, UUID], create_field=True, **kwargs
) -> Question:
    """
    Update a Question's scalar fields and/or relationships.

    Args:
        session: Database session.
        question_id: The question's identifier (UUID or string convertible to UUID).
        create_field: If True, create related records on-the-fly when assigning relationships.
        **kwargs: Field values to set on the Question (both columns and relationships).

    Returns:
        The updated Question instance.

    Raises:
        ValueError: If the Question does not exist.
        TypeError: If relationship values are of incorrect types and create_field=False.
    """
    question = session.get(Question, question_id)
    if not question:
        raise ValueError("Question not found")

    mapper = sa_inspect(Question)

    for key, value in kwargs.items():
        try:
            prop = mapper.get_property(key)
            is_rel = is_relationship(Question, key)
        except Exception:
            continue

        if not is_rel:
            setattr(question, key, value)
            continue
        else:
            target_cls = prop.mapper.class_
            if prop.uselist:
                if not all(isinstance(v, target_cls) for v in value):
                    if not create_field:
                        raise TypeError(f"{key} expects list[{target_cls.__name__}]")
                    else:
                        value = [
                            resolve_or_create(session, target_cls, v, create_field)[0]
                            for v in value
                        ]
                setattr(question, key, list(value))
            else:
                if value is not None and not isinstance(value, target_cls):
                    if not create_field:
                        raise TypeError(f"{key} expects {target_cls.__name__} or None")
                    else:
                        value = resolve_or_create(
                            session, target_cls, value, create_field
                        )[0]
                setattr(question, key, value)
            continue
    session.commit()
    session.refresh(question)
    return question


# # Todo make this a bit more general and handle
def filter_questions(
    session,
    filters,
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
