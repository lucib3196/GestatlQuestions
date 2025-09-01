# Stdlib
from typing import Dict, List, Sequence, Union
from uuid import UUID
import asyncio

# Third-party
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlmodel import select
from starlette import status

# Internal
from backend_api.data import language_db as l_service
from backend_api.data import qtype_db as qtype_service
from backend_api.data import topic_db as t_service
from backend_api.data.database import SessionDep
from backend_api.model.question_model import Language, QType, Question, Topic
from backend_api.utils import *
from backend_api.core.logging import logger


def get_question_id_UUID(question_id) -> UUID:
    """Validate and convert a question_id to UUID or raise HTTP 400."""
    try:
        if isinstance(question_id, UUID):
            return question_id
        else:
            return UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


def create_question(
    payload: Union[Question, dict], session: SessionDep, create=False
) -> Question:

    if payload is None:
        raise ValueError("Payload cannot be None")
    try:
        if isinstance(payload, Question):
            title = payload.title
            ai_generated = payload.ai_generated
            is_adaptive = payload.isAdaptive
            created_by = payload.createdBy
            user_id = payload.user_id
            t_incoming = getattr(payload, "topics", None)
            q_incoming = getattr(payload, "qtype", None)
            l_incoming = getattr(payload, "languages")
        else:
            title = payload.get("title")
            ai_generated = payload.get("ai_generated")
            is_adaptive = payload.get("isAdaptive")
            created_by = payload.get("createdBy")
            user_id = payload.get("user_id")
            t_incoming = payload.get("topics")
            q_incoming = payload.get("qtype")
            l_incoming = payload.get("languages")

        question = Question(
            title=title,
            ai_generated=ai_generated,
            isAdaptive=bool(is_adaptive),
            createdBy=created_by,
            user_id=user_id,
            topics=[],  # set after validation
            qtypes=[],
        )
    except Exception as e:
        raise ValueError(e)

    # Handle Topics
    topic_objs: List[Topic] = []
    if t_incoming:
        if all(isinstance(t, Topic) for t in t_incoming):
            topic_objs = list(t_incoming)
        elif all(isinstance(t, str) for t in t_incoming):
            names = normalize_names(t_incoming)
            found = t_service.get_topics_by_name(session, names=names)
            found_names = {t.name for t in found}

            missing = sorted(set(names) - found_names)
            if missing and not create:
                raise ValueError(f"Unknown topic(s): {', '.join(missing)}")
            elif not missing or create:
                for m in missing:
                    found.extend([t_service.create_topic(session, m)])
                topic_objs = found
        else:
            raise TypeError("topics must be a list of str or a list of Topic objects")

    qtype_obj: List[QType] = []
    if q_incoming:
        if all(isinstance(q, QType) for q in q_incoming):
            qtype_obj = list(q_incoming)
        elif all(isinstance(q, str) for q in q_incoming):
            names = normalize_names(q_incoming)
            found = qtype_service.get_qtypes_by_name(session, names=names)
            found_names = {q.name for q in found}

            missing = sorted(set(names) - found_names)
            if missing and not create:
                raise ValueError(f"Unknown qtype(s): {', '.join(missing)}")
            elif not missing or create:
                for m in missing:
                    found.extend([qtype_service.create_qtype(session, m)])
                qtype_obj = found
        else:
            raise TypeError("topics must be a list of str or a list of Topic objects")

    language_obj: List[Language] = []
    if l_incoming:
        if all(isinstance(q, Language) for q in l_incoming):
            language_obj = list(l_incoming)
        elif all(isinstance(q, str) for q in l_incoming):
            names = normalize_names(l_incoming)
            found = l_service.get_languages_by_name(session, names=names)
            found_names = {q.name for q in found}

            missing = sorted(set(names) - found_names)
            if missing and not create:
                raise ValueError(f"Unknown language(s): {', '.join(missing)}")
            elif not missing or create:
                for m in missing:
                    found.extend([l_service.create_language(session, m)])
                language_obj = found
        else:
            raise TypeError("topics must be a list of str or a list of Topic objects")

    question.topics = topic_objs
    question.qtypes = qtype_obj
    question.languages = language_obj

    session.add(question)
    session.commit()
    session.refresh(question)
    return question


def delete_all_questions(session: SessionDep):
    questions = session.exec(select(Question)).all()
    for q in questions:
        session.delete(q)
        session.commit()
        session.flush()


def delete_question_by_id(question_id: Union[str, UUID], session: SessionDep):
    question = get_question_by_id(question_id, session)
    if not question:
        return None
    else:
        session.delete(question)
        session.commit()
        session.flush()


def get_all_questions(
    session: SessionDep, offset: int = 0, limit: int = 100
) -> Sequence[Question]:
    return session.exec(select(Question).offset(offset).limit(limit)).all()


def get_question_by_id(question_id: Union[str, UUID], session: SessionDep):
    qid = get_question_id_UUID(question_id)
    question = session.exec(select(Question).where(Question.id == qid)).first()
    return question


def safe_python_type(col):
    try:
        return col.type.python_type
    except (NotImplementedError, AttributeError):
        return object


# Update
def update_question(
    session, question_id: Union[str, UUID], create_field=True, **kwargs
) -> Question:
    question = session.get(Question, question_id)
    if not question:
        raise ValueError("Question not found")

    mapper = sa_inspect(Question)

    for key, value in kwargs.items():
        # skip unknown attributes
        try:
            prop = mapper.get_property(key)
        except Exception:
            continue

        if isinstance(prop, ColumnProperty):
            # Needs to add check that the type and value are being set correctly

            col = prop.columns[0]
            setattr(question, key, value)
            continue
        elif isinstance(prop, RelationshipProperty):
            target_cls = prop.mapper.class_
            if prop.uselist:
                if not all(isinstance(v, target_cls) for v in value):
                    if not create_field:
                        raise TypeError(f"{key} expects list[{target_cls.__name__}]")
                    else:
                        value = [
                            resolve_or_create(session, target_cls, v, create_field)
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
                        )
                setattr(question, key, value)
            continue
    session.commit()
    session.refresh(question)
    return question


async def get_question_data(
    question_id: Union[str, UUID],
    session: SessionDep,
    rels: List[str] = ["topics", "qtypes", "languages"],
) -> Dict[str, Any]:
    stmt = select(Question).where(Question.id == get_uuid(question_id))
    result = session.exec(stmt).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    data = get_model_relationship_data(result, rels)
    return data


async def get_all_question_data(
    session: SessionDep, offset: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    results: Sequence[Question] = get_all_questions(session, offset=offset, limit=limit)
    logger.debug("These are the questions %s", results)
    tasks = [get_question_data(question_id=r.id, session=session) for r in results]
    return await asyncio.gather(*tasks)


# Hybrid
def get_question_topics(
    question_id: Union[str, UUID], session: SessionDep
) -> Sequence[Topic]:
    question = get_question_by_id(question_id, session)
    if question and question.topics:
        return question.topics
    else:
        return []


# Todo make this a bit more general and handle
def filter_questions(session, partial_match=True, **kwargs):
    mapper = sa_inspect(Question)
    filters = []

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
