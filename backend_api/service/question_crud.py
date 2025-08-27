# Standard library
import json
from json import JSONDecodeError
from typing import Optional, Union, Literal
from uuid import UUID
from pathlib import Path

# Third-party
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import select
from starlette import status
import tempfile
from typing import Sequence

# Local
from backend_api.core.logging import logger
from backend_api.data.database import SessionDep
from backend_api.model.question_model import (
    File,
    Question,
    QuestionDict,
    QuestionMetaNew,
)
from backend_api.model.topic_model import Topic
from code_runner.run_server import run_generate
from backend_api.data import question_db as qdata


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
            status_code=status.HTTP_400_BAD_REQUEST,
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
        if results is None:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT, detail="Question does not exist"
            )
        return results
    except ValueError or HTTPException as e:
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error {str(e)}"
        )


async def edit_question_meta(
    question_id: Union[str, UUID], session: SessionDep, **kwargs
):
    try:
        updated_question = qdata.update_question(session, question_id, **kwargs)
        return updated_question
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating Question {question_id}: {str(e)}",
        )


async def filter_questions_meta(session: SessionDep, **kwargs) -> Sequence[Question]:
    try:
        questions = qdata.filter_questions(session, **kwargs)
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT, detail="No questions fit filter"
            )
        return questions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown Error str(e)",
        )


# Transitioning


async def get_question_topics(session: SessionDep, question_id: str) -> list[str]:
    """Return list of topic names for a question."""
    qid: UUID = get_question_id_UUID(question_id)

    stmt = (
        select(Question)
        .options(selectinload(Question.topics))  # eager-load topics # type: ignore
        .where(Question.id == qid)
    )
    question = session.exec(stmt).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        )

    return [t.name for t in question.topics]  # or return question.topics


async def get_question_qmeta(question_id: str, session: SessionDep):
    """Fetch and validate qmeta.json for a question, returning QuestionMetaNew."""
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


async def filter_questions(session: SessionDep, qfilter: QuestionDict):
    """Apply dynamic filters to Question based on qfilter."""
    filters = []
    for key, value in qfilter.items():
        logger.debug("Filter: %s = %r", key, value)

        col = getattr(Question, key, None)
        if not col or value in (None, "", []):
            continue

        # For not full search just alike
        if key == "title":
            vals = value if isinstance(value, (list, tuple, set)) else [value]
            filters.append(or_(*[Question.title.ilike(f"%{v}%") for v in vals if v]))  # type: ignore
            continue

        # handle cases where there is a list
        if isinstance(value, (list, tuple, set)):
            filters.append(or_(*[col == v for v in value]))
            logger.debug("Value %s", value)
        else:
            filters.append(col == value)

    stmt = select(Question)
    if filters:
        stmt = stmt.where(*filters)  # AND across keys, OR within each key
    return session.exec(stmt).all()


# =========================
# Update
# =========================


async def add_topic_to_question(
    question_id: str,
    topic_name: str,
    session: SessionDep,
) -> Question:
    """Attach a Topic (creating if necessary) to a Question."""
    # normalize inputs
    name = (topic_name or "").strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic name must be a non-empty string.",
        )

    # resolve / validate question id
    question_uuid: UUID = get_question_id_UUID(question_id)

    # fetch question
    question: Optional[Question] = session.exec(
        select(Question).where(Question.id == question_uuid)
    ).first()
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {question_uuid} not found.",
        )

    # get or create topic (unique by name)
    topic: Optional[Topic] = session.exec(
        select(Topic).where(Topic.name == name)
    ).first()

    if topic is None:
        topic = Topic(name=name)
        session.add(topic)
        try:
            session.commit()
        except IntegrityError:
            # another request may have created it concurrently
            session.rollback()
            topic = session.exec(select(Topic).where(Topic.name == name)).one()
        finally:
            session.refresh(topic)

    # make sure question.topics is a list (older schemas might have Optional)
    if getattr(question, "topics", None) is None:
        question.topics = []

    # avoid duplicate link
    if not any(t.id == topic.id for t in question.topics):
        question.topics.append(topic)
        session.add(question)
        session.commit()
        session.refresh(question)

    return question


# =========================
# Delete
# =========================


# =========================
# Composite Ops
# =========================


async def add_question_and_files(
    question: Question, files: dict[str, Union[str, dict]], session: SessionDep
) -> Question:
    """Create a question and (conditionally) add files."""
    question = await add_question(question, session)
    for filename, contents in files.items():
        if isinstance(contents, (dict, list)):
            contents = json.dumps(contents)

            file_obj = File(
                filename=filename, content=contents, question_id=question.id
            )

            await add_file(file_obj, session)
    return question


# Running Questions
async def run_server(
    question_id: Union[str, UUID],
    code_language: Literal["python", "javascript"],
    session: SessionDep,
):
    mapping_db = {"python": "server_py", "javascript": "server_js"}
    mapping_filename = {"python": "server.py", "javascript": "server.js"}

    if (isinstance, str):
        question_id = get_question_id_UUID(question_id)

    # Validate language
    if code_language not in mapping_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported code language"
        )
    server_file = await get_question_file(
        question_id, mapping_db[code_language], session
    )
    server_content = server_file.content
    if server_content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Server file content is empty"
        )
    if isinstance(server_content, (dict, list)):
        try:
            server_content = json.dumps(server_content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to serialize server content: {e}",
            )
    elif not isinstance(server_content, str):
        server_content = str(server_content)
    # Write to a temp file and execute
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / mapping_filename[code_language]
            file_path.write_text(server_content, encoding="utf-8")
            logger.debug("Executing server code at %s", file_path)

            try:
                output = run_generate(str(file_path), isTesting=False)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Execution error: {e}",
                )

            return output
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}",
        )
