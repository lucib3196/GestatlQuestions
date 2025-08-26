# Standard library
from typing import Any, Optional

# Third-party
from fastapi import HTTPException
from starlette import status

# Local
from ai_workspace.agents.code_generators.v4_5.main_text import (
    OutputState as CodeResults,
)
from ai_workspace.utils import to_serializable
from backend_api.data.database import SessionDep
from backend_api.model.question_model import File, Question
from backend_api.service import db_question as core_db
from backend_api.utils.utils import normalize_name, to_bool
from backend_api.service import (
    get_or_create_language,
    get_or_create_Qtype,
    get_or_create_topic,
)
from typing import Any


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
        title=title or cr.qmeta.title,
        isAdaptive=is_adaptive,
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
    if hasattr(cr.qmeta, "topic"):
        raw_topics = cr.qmeta.topic or []
        norm_topics = {n for n in (normalize_name(t) for t in raw_topics) if n}
        if getattr(question, "topics", None) is None:
            question.topics = []
        if norm_topics:
            for n in norm_topics:
                topic, existing = await get_or_create_topic(session, n)
                question.topics.append(topic)

    # Add the languages
    if hasattr(cr.qmeta, "language"):
        raw_langauges = cr.qmeta.language or []
        norm_languages = {n for n in (normalize_name(l) for l in raw_langauges) if n}
        if getattr(question, "languages", None) is None:
            question.languages = []
        if norm_languages:
            for l in norm_languages:
                language, existing = await get_or_create_language(session, l)
                question.languages.append(language)

    if hasattr(cr.qmeta, "qtype"):
        raw_qtypes = cr.qmeta.qtype or []
        norm_qtypes = {n for n in (normalize_name(l) for l in raw_qtypes) if n}

        # Add qtypes
        if getattr(question, "qtypes", None) is None:
            question.qtypes = []
        if norm_qtypes:
            for n in norm_qtypes:
                qtype, existing = await get_or_create_Qtype(session, n)
                question.qtypes.append(qtype)

    session.add(question)
    session.commit()
    session.refresh(question)
    return question


from ai_workspace.agents.code_generators.v5.main import CodeGen


async def add_generated_dbV5(
    cr: CodeGen,
    user_id: int,
    title: str,
    session: SessionDep,
    ai_generated: bool = True,
):
    try:
        is_adaptive = to_bool(cr.metadata.isAdaptive if cr.metadata else False)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    question_obj = Question(
        user_id=user_id,
        title=title or cr.metadata.title,  # type: ignore
        isAdaptive=is_adaptive,
        ai_generated=ai_generated,
    )
    question = await core_db.add_question(question_obj, session)
    if not getattr(question, "id", None):
        session.refresh(question)

    for filename, content in cr.files_data.items():
        if isinstance(content, dict):
            content = to_serializable(content)
        session.add(File(filename=filename, content=content, question_id=question.id))

    if hasattr(cr.metadata, "topics"):
        raw_topics = cr.metadata.topics or []
        norm_topics = {n for n in (normalize_name(t) for t in raw_topics) if n}
        if getattr(question, "topics", None) is None:
            question.topics = []
        if norm_topics:
            for n in norm_topics:
                topic, existing = await get_or_create_topic(session, n)
                question.topics.append(topic)
                
    if hasattr(cr.metadata, "language"):
        raw_langauges = cr.metadata.language or []
        norm_languages = {n for n in (normalize_name(l) for l in raw_langauges) if n}
        if getattr(question, "languages", None) is None:
            question.languages = []
        if norm_languages:
            for l in norm_languages:
                language, existing = await get_or_create_language(session, l)
                question.languages.append(language)
        raw_qtypes = cr.metadata.qtype or []
        norm_qtypes = {n for n in (normalize_name(l) for l in raw_qtypes) if n}


    if hasattr(cr.metadata, "qtype"):
        raw_qtypes = cr.metadata.qtype or []
        norm_qtypes = {n for n in (normalize_name(l) for l in raw_qtypes) if n}

        # Add qtypes
        if getattr(question, "qtypes", None) is None:
            question.qtypes = []
        if norm_qtypes:
            for n in norm_qtypes:
                qtype, existing = await get_or_create_Qtype(session, n)
                question.qtypes.append(qtype)
                

    session.add(question)
    session.commit()
    session.refresh(question)
    return question
