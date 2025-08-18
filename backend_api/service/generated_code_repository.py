# Standard library
import json
from typing import Any, Optional

# Third-party
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from starlette import status

# Local
from ai_workspace.agents.code_generators.v4_5.main_text import (
    OutputState as CodeResults,
)
from ai_workspace.utils import to_serializable
from backend_api.data.database import SessionDep
from backend_api.model.questions_models import File, Question, Topic
from backend_api.service import db_question as core_db
from backend_api.utils.utils import _normalize_topic_name, to_bool


async def add_generated_db(
    cr: CodeResults, user_id: int, title: Optional[str], session: SessionDep
) -> Question:
    # Basic conversion and checks
    try:
        is_adaptive = to_bool(cr.qmeta.isAdaptive)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    question_obj = Question(
        user_id=user_id,
        qtype=cr.qmeta.qtype,
        title=title or cr.qmeta.title,
        isAdaptive=is_adaptive,
        language=cr.qmeta.language,
        ai_generated=True,
    )

    # Add question to db
    question = await core_db.add_question(question_obj, session)
    if not getattr(question, "id", None):
        session.refresh(question)

    # Adds all the generated files to the database
    files_payload = cr.files.model_dump(exclude_none=True)
    for filename, content in files_payload.items():
        if hasattr(content, "model_dump"):
            content = content.model_dump(exclude_none=True)
        elif isinstance(content, (dict, list)):
            pass
        elif not isinstance(content, str):
            content = str(content)

        session.add(File(filename=filename, content=content, question_id=question.id))  # type: ignore

    try:
        qmeta_json: Any = to_serializable(cr.qmeta)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid qmeta: {e}"
        )
    session.add(
        File(filename="qmeta.json", content=qmeta_json, question_id=question.id)
    )

    # Add topics
    raw_topics = cr.qmeta.topic or []
    norm_names = {n for n in (_normalize_topic_name(t) for t in raw_topics) if n}
    if norm_names:
        existing = session.exec(select(Topic).where(Topic.name.in_(norm_names))).all()  # type: ignore
        by_name = {t.name: t for t in existing}

        # Gets topics that are not yet in the database
        missing = [n for n in norm_names if n not in by_name]
        for name in missing:
            t = Topic(name=name)
            session.add(t)
            try:
                session.flush()  # get ID without full commit
            except IntegrityError:
                session.rollback()
                t = session.exec(select(Topic).where(Topic.name == name)).one()
            by_name[name] = t
        if getattr(question, "topics", None) is None:
            question.topics = []

        existing_ids = {t.id for t in question.topics}
        to_add = [t for t in by_name.values() if t.id not in existing_ids]
        if to_add:
            question.topics.extend(to_add)
            session.add(question)

    session.commit()
    session.refresh(question, attribute_names=["topics"])
    return question
