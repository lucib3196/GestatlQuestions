# --- Standard Library ---
from typing import List, Literal, Optional, Union, Annotated
from uuid import UUID
from fastapi import UploadFile

# --- Third-Party ---
from fastapi import APIRouter, HTTPException
from starlette import status

# --- Internal ---
from src.api.database import SessionDep
from src.api.models.question_model import Question, QuestionMeta
from src.api.response_models import *
from src.api.service import question_crud
from src.api.service import question_storage_service as qs
from src.utils import normalize_kwargs
from src.api.service import file_management as fm
from fastapi import FastAPI, File, UploadFile

from fastapi import Form
import json


router = APIRouter(prefix="/file_uploads", tags=["file_uploads"])


class UploadQuesiton(BaseModel):
    question: Union[Question, dict]
    additional_metadata: Optional[AdditionalQMeta] = None


@router.post("/create_question/upload")
async def create_question_file_upload(
    session: SessionDep,
    question: Optional[str] = Form(None),  # incoming as string
    additional_metadata: Optional[str] = Form(None),
    files: list[UploadFile] = File(...),
    save_dir: Literal["local", "firebase"] = "local",
):
    try:
        # Parse JSON strings
        q_data = json.loads(str(question))
        if isinstance(q_data, Question):
            base_question = q_data.model_dump()
        elif isinstance(question, dict):
            base_question = question
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="expected dict or type Question",
            )
        meta_data = None
        if additional_metadata:
            meta_data = AdditionalQMeta.model_validate(json.loads(additional_metadata))
            base_question = {**base_question, **meta_data.model_dump()}

        q_created = await question_crud.create_question(base_question, session)
        if save_dir == "local":
            await qs.set_directory(q_created.id, session)
        elif save_dir == "firebase":
            raise NotImplementedError("Have not implemented firebase functionality")

        # Validate files
        file_data_list = []

        for f in files:
            # Validate UploadFile (assuming fm.validate_file returns UploadFile)
            f = await fm.validate_file(f)
            content = await f.read()
            await f.seek(0)

            # Wrap in FileData
            fd = FileData(filename=str(f.filename), content=content)

            file_data_list.append(fd)
        return {"detail": "okay", "question": q_created, "metadata": meta_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{qid}/upload_file/")
async def upload_files_to_question(
    qid: str | UUID,
    session: SessionDep,
    files: list[UploadFile] = File(...),
    save_dir: Literal["local", "firebase"] = "local",
):
    try:
        # Validate files
        file_data_list = []
        for f in files:
            # Validate UploadFile (assuming fm.validate_file returns UploadFile)
            f = await fm.validate_file(f)
            content = await f.read()
            await f.seek(0)

            # Wrap in FileData
            fd = FileData(filename=str(f.filename), content=content)

            file_data_list.append(fd)
        response = await qs.write_files_to_directory(qid, file_data_list, session)
        return {"detail": "okay", "files": response.files}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
