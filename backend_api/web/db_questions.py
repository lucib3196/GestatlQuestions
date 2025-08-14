from backend_api.service import db_question as service
from fastapi import APIRouter, Depends
from backend_api.data.database import get_session
from sqlmodel import Session
from typing import List, Literal
from backend_api.model.questions_models import QuestionMetaNew
from fastapi import UploadFile
from backend_api.model.questions_models import Question, QuestionDict, File
from uuid import UUID
from backend_api.data.database import SessionDep
from fastapi import HTTPException
from sqlmodel import select
import tempfile
from pathlib import Path
from code_runner.run_server import run_generate
import json

router = APIRouter(prefix="/db_questions")


@router.post("get_all_questions/{offset}/{limit}", response_model=List[Question])
async def get_all_questions(offset: int, limit: int, session=Depends(get_session)):
    return await service.get_all_questions(session, offset=offset, limit=limit)


@router.get("/get_question/qmeta/{question_id}", response_model=QuestionMetaNew)
async def get_question_qmeta(question_id: str, session=Depends(get_session)):
    return await service.get_question_qmeta(question_id, session)


@router.post("/run_server/{question_id}/{code_language}")
async def run_server(
    question_id: UUID,
    code_language: Literal["python", "javascript"],
    session=Depends(get_session),
):
    """
    Load the stored server code for the given question & language, write it to a temp file,
    run it via `run_generate`, and return the result. Includes input validation and error handling.
    """
    mapping_db = {"python": "server_py", "javascript": "server_js"}
    mapping_filename = {"python": "server.py", "javascript": "server.js"}

    # Validate language
    if code_language not in mapping_db:
        raise HTTPException(status_code=400, detail="Unsupported code language")

    # Fetch the file row
    stmt = (
        select(File)
        .where(File.question_id == question_id)
        .where(File.filename == mapping_db[code_language])
    )
    result = session.exec(stmt).first()
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Server file not found for the given question/language",
        )

    # Normalize content to a string
    content = result.content
    if content is None:
        raise HTTPException(status_code=404, detail="Server file content is empty")

    if isinstance(content, (dict, list)):
        try:
            content = json.dumps(content)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to serialize server content: {e}"
            )
    elif not isinstance(content, str):
        content = str(content)

    # Write to a temp file and execute
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / mapping_filename[code_language]
            file_path.write_text(content, encoding="utf-8")

            try:
                output = run_generate(file_path, isTesting=False)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Execution error: {e}")

            return output
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.get("/get_question_files/{question_id}")
async def get_question_files(question_id: str, session=Depends(get_session)):
    try:
        question_uuid = UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    stmt = select(File).where(File.question_id == question_uuid)
    result = session.exec(stmt).all()
    return result


@router.post("/filter_question", response_model=List[Question])
async def get_filtered_questions(qfilter: QuestionDict, session=Depends(get_session)):

    return await service.filter_questions(session, qfilter)


from pydantic import BaseModel


class UpdateFile(BaseModel):
    title: str
    filename: str
    newcontent: str


@router.post("/update_file/")
async def update_file(file_update: UpdateFile, session=Depends(get_session)):
    return await service.update_file(
        question_id=file_update.title,
        filename=file_update.filename,
        newcontent=file_update.newcontent,
        session=session,
    )


@router.post("/delete_question")
async def delete_question(question_id: str, session: SessionDep):
    # convert
    try:
        question_uuid = UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    return await service.delete_question(question_uuid, session)
