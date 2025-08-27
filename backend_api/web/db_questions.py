from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, List, Literal, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from backend_api.core.logging import logger
from backend_api.data.database import SessionDep, get_session
from backend_api.model.question_model import (
    File,
    Question,
    QuestionDict,
    QuestionMetaNew,
)
from backend_api.service import question_crud as service
from code_runner.run_server import run_generate
from typing import Any, List, Literal, Optional
from pydantic import BaseModel
from code_runner.models import CodeRunResponse


router = APIRouter(prefix="/db_questions")


# ------------------------- Routes ------------------------- #


@router.post("/get_all_questions/{offset}/{limit}", response_model=List[Question])
async def get_all_questions(
    offset: int,
    limit: int,
    session=Depends(get_session),
):
    """Return paginated questions."""
    return await service.get_all_questions(session, offset=offset, limit=limit)


@router.get("/get_question/qmeta/{question_id}", response_model=QuestionMetaNew)
async def get_question_qmeta(
    question_id: str,
    session=Depends(get_session),
):
    """Return the parsed qmeta.json for a question."""
    return await service.get_question_qmeta(question_id, session)


@router.get("/get_question/{question_id}/file/{filename}")
async def get_question_file(
    question_id: str, filename: str, session=Depends(get_session)
):

    return await service.get_question_file(question_id, filename, session)


@router.post("/run_server/{question_id}/{code_language}")
async def run_server(
    question_id: Union[str, UUID],
    code_language: Literal["python", "javascript"],
    session=Depends(get_session),
):
    """
    Load stored server code for the given question & language, write to a temp file,
    run via `run_generate`, and return the result.
    """
    return await coreDb_service.run_server(question_id, code_language, session)


# ------------------------- Run Test (kept & implemented) ------------------------- #


class TestArgs(BaseModel):
    questions_id: List[str]
    server_type: Literal["javascript", "python"]


class RunTestItem(BaseModel):
    question_id: str
    server_type: Literal["javascript", "python"]
    status: Literal["ok", "error"]
    output: Optional[CodeRunResponse] = None
    error: Optional[str] = None


class RunTestResponse(BaseModel):
    success_count: int
    failure_count: int
    results: List[RunTestItem]


@router.post("/run_test/", response_model=RunTestResponse)
async def run_test(
    test_args: TestArgs,
    session=Depends(get_session),
):
    """
    Run server code in *test mode* for a batch of questions.
    For each question:
      - Load the stored server code (python/js)
      - Write to a temp file
      - Invoke run_generate(..., isTesting=True)
    Returns per-question results without failing the whole batch.
    """
    mapping_db = {"python": "server_py", "javascript": "server_js"}
    mapping_filename = {"python": "server.py", "javascript": "server.js"}

    server_type = test_args.server_type
    if server_type not in mapping_db:
        raise HTTPException(status_code=400, detail="Unsupported server_type")

    items: List[RunTestItem] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        for qid_str in test_args.questions_id:
            # Default item (we’ll mutate fields below)
            item_data: dict[str, Any] = {
                "question_id": qid_str,
                "server_type": server_type,
                "status": "error",
                "output": None,
                "error": None,
            }

            # Validate UUID
            try:
                qid = UUID(qid_str)
            except ValueError:
                item_data["error"] = "Invalid UUID format"
                items.append(RunTestItem.model_validate(item_data))
                continue

            # Fetch file row
            stmt = (
                select(File)
                .where(File.question_id == qid)
                .where(File.filename == mapping_db[server_type])
            )
            row = session.exec(stmt).first()
            if row is None:
                item_data["error"] = "Server file not found for this question/language"
                items.append(RunTestItem.model_validate(item_data))
                continue

            content = row.content
            if content is None:
                item_data["error"] = "Server file content is empty"
                items.append(RunTestItem.model_validate(item_data))
                continue

            # Normalize to string
            try:
                if isinstance(content, (dict, list)):
                    content = json.dumps(content)
                elif not isinstance(content, str):
                    content = str(content)
            except Exception as e:
                item_data["error"] = f"Failed to serialize server content: {e}"
                items.append(RunTestItem.model_validate(item_data))
                continue

            # Write and execute
            try:
                file_path = tmpdir_path / mapping_filename[server_type]
                file_path.write_text(content, encoding="utf-8")
                logger.debug("Testing server code at %s", file_path)

                output = run_generate(str(file_path), isTesting=True)

                # Ensure output matches CodeRunResponse
                if isinstance(output, CodeRunResponse):
                    item_data["status"] = "ok"
                    item_data["output"] = output
                elif isinstance(output, dict):
                    try:
                        item_data["status"] = "ok"
                        item_data["output"] = CodeRunResponse.model_validate(output)
                    except Exception as ve:
                        item_data["status"] = "error"
                        item_data["error"] = f"Unexpected output shape: {ve}"
                else:
                    item_data["status"] = "error"
                    item_data["error"] = (
                        f"Unexpected output type: {type(output).__name__}"
                    )

            except Exception as e:
                item_data["status"] = "error"
                item_data["error"] = f"Execution error: {e}"

            items.append(RunTestItem.model_validate(item_data))

    success_count = sum(1 for r in items if r.status == "ok")
    failure_count = len(items) - success_count

    return RunTestResponse(
        success_count=success_count,
        failure_count=failure_count,
        results=items,
    )


# ------------------------- Misc routes ------------------------- #


@router.get("/get_question_files/{question_id}", response_model=List[File])
async def get_question_files(
    question_id: str,
    session=Depends(get_session),
):
    """List all files stored for a question."""
    try:
        question_uuid = UUID(question_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID format"
        )

    stmt = select(File).where(File.question_id == question_uuid)
    return session.exec(stmt).all()


@router.post("/filter_question", response_model=List[Question])
async def get_filtered_questions(
    qfilter: QuestionDict,
    session=Depends(get_session),
):
    """Filter questions using the provided criteria."""
    return await service.filter_questions(session, qfilter)


class UpdateFile(BaseModel):
    title: str
    filename: str
    newcontent: str


@router.post("/update_file/")
async def update_file(
    file_update: UpdateFile,
    session=Depends(get_session),
):
    """Update a stored file's content for a question."""
    return await service.update_file(
        question_id=file_update.title,
        filename=file_update.filename,
        newcontent=file_update.newcontent,
        session=session,
    )


@router.post("/delete_question")
async def delete_question(
    question_id: str,
    session=Depends(get_session),
):
    """Delete a question by id."""
    try:
        question_uuid = UUID(question_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid UUID format"
        )
    return await service.delete_question(question_uuid, session)


@router.post("/add_topic/{question_id}/{topic_name}")
async def add_topic_to_question(
    question_id: str,
    topic_name: str,
    session=Depends(get_session),
):
    """Attach a topic to a question (creates topic if missing)."""
    return await service.add_topic_to_question(
        question_id=question_id, topic_name=topic_name, session=session
    )


@router.get("/get_topic/{question_id}", response_model=List[str])
async def get_question_topics(
    question_id: str,
    session=Depends(get_session),
):
    """Return topic names associated with a question."""
    return await service.get_question_topics(question_id=question_id, session=session)


# Donwload Utilits
from backend_api.service import question_crud as coreDb_service
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import io, zipfile, pathlib


class QuestionIds(BaseModel):
    question_ids: List[str]


def normalize_content(content: Any):
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return json.dumps(content)
    else:
        "Unknown"


import re


def safe_filename(name: str) -> str:
    # prevent path traversal / weird chars
    name = name or "untitled"
    name = name.replace("\\", "/").split("/")[-1]
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def to_bytes(content) -> bytes:
    if isinstance(content, (bytes, bytearray)):
        return bytes(content)
    if isinstance(content, str):
        return content.encode("utf-8")
    # fallback: JSON serialize
    return json.dumps(content, ensure_ascii=False, indent=2).encode("utf-8")


@router.post("/download_questions/")
async def download_questions(question_ids: QuestionIds, session=Depends(get_session)):
    ids = question_ids.question_ids or []
    if not ids:
        raise HTTPException(status_code=400, detail="No question_ids provided")

    valid_uuids, missing = [], []
    for q in ids:
        try:
            uid = coreDb_service.get_question_id_UUID(q)
            if uid:
                valid_uuids.append(uid)
            else:
                missing.append(q)
        except Exception:
            missing.append(q)
    if not valid_uuids:
        raise HTTPException(status_code=404, detail="No Valid questions found")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        manifest: list[dict] = []

        for qid in valid_uuids:
            files = await coreDb_service.get_all_files(qid, session)
            qtile = session.exec(
                select(Question.title).where(Question.id == qid)
            ).first()
            q_prefix = f"{qtile}/" or "UntitledQuestion"

            for f in files:
                fname = safe_filename(getattr(f, "filename", "file"))
                data = to_bytes(normalize_content(getattr(f, "content", b"")))
                arcname = q_prefix + fname
                z.writestr(arcname, data)
                manifest.append(
                    {"question_id": str(qid), "file": arcname, "size": len(data)}
                )

        z.writestr(
            "MANIFEST.json",
            json.dumps(
                {"count": len(manifest), "missing": missing},
                ensure_ascii=False,
                indent=2,
            ),
        )

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="questions.zip"'},
    )
