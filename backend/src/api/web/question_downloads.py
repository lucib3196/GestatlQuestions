from __future__ import annotations

# --- Standard Library ---
from typing import List, Literal, Optional, Union
from uuid import UUID

# --- Third-Party ---
from fastapi import APIRouter, HTTPException
from starlette import status

# --- Internal ---
from src.api.database import SessionDep
from src.api.models.question_model import Question, QuestionMeta
from src.api.response_models import *
from src.api.service.crud import question_crud
from src.api.service import question_storage_service as qs
from src.utils import normalize_kwargs

import json
from src.api.service.crud import question_crud as qs
router = APIRouter(prefix="/question_crud", tags=["question_crud"])

# Donwload Utilits
from src.api.service.crud import question_crud as coreDb_service
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


# @router.post("/download_questions/")
# async def download_questions(question_ids: QuestionIds, session=Depends(get_session)):
#     ids = question_ids.question_ids or []
#     if not ids:
#         raise HTTPException(status_code=400, detail="No question_ids provided")

#     valid_uuids, missing = [], []
#     for q in ids:
#         try:
#             uid = await qs.get_question_by_id(q, session)
#             if uid:
#                 valid_uuids.append(uid)
#             else:
#                 missing.append(q)
#         except Exception:
#             missing.append(q)
#     if not valid_uuids:
#         raise HTTPException(status_code=404, detail="No Valid questions found")

#     buf = io.BytesIO()
#     with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
#         manifest: list[dict] = []

#         for qid in valid_uuids:
#             files = await qs.get_all_files(qid, session)
#             qtile = session.exec(
#                 select(Question.title).where(Question.id == qid)
#             ).first()
#             q_prefix = f"{qtile}/" or "UntitledQuestion"

#             for f in files:
#                 fname = safe_filename(getattr(f, "filename", "file"))
#                 data = to_bytes(normalize_content(getattr(f, "content", b"")))
#                 arcname = q_prefix + fname
#                 z.writestr(arcname, data)
#                 manifest.append(
#                     {"question_id": str(qid), "file": arcname, "size": len(data)}
#                 )

#         z.writestr(
#             "MANIFEST.json",
#             json.dumps(
#                 {"count": len(manifest), "missing": missing},
#                 ensure_ascii=False,
#                 indent=2,
#             ),
#         )

#     buf.seek(0)
#     return StreamingResponse(
#         buf,
#         media_type="application/zip",
#         headers={"Content-Disposition": 'attachment; filename="questions.zip"'},
#     )
