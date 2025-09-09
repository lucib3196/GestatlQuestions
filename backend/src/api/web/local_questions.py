from pydantic import BaseModel, Field
from typing import List, Union, Literal, Optional
from fastapi import APIRouter, Depends
from api.service import local_questions as service
from api.models.question_model import QuestionMeta, QuestionMetaNew
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import json
from fastapi import UploadFile, File


router = APIRouter(prefix="/local_questions")


class QuestionFilter(BaseModel):
    topic: Optional[str] = None
    qtype: Optional[Literal["numeric", "multiple_choice"]] = None
    isAdaptive: Optional[bool] = None

    relevant_courses: Optional[str] = None
    tags: Optional[str] = None
    prereqs: Optional[str] = None

    title: Optional[str] = None
    ai_generated: Optional[bool] = None
    language: Optional[str] = None


class UniqueValueCount(BaseModel):
    value: str
    count: int


class UniqueValueCountList(BaseModel):
    key: str
    values: List[UniqueValueCount]


@router.get("/get_all_metadata", response_model=Union[List[QuestionMeta]])
async def get_all_metadata():
    return service.get_all_question_meta()


@router.get(
    "/filter_questions/new_format", response_model=Optional[List[QuestionMetaNew]]
)
async def filter_questions_new(filters: QuestionFilter = Depends()):
    active_filters = {k: v for k, v in filters.dict().items() if v is not None}
    return service.filter_questions_new(active_filters)


@router.get("/filter_questions", response_model=Optional[List[QuestionMeta]])
async def filter_questions(filters: QuestionFilter = Depends()):
    active_filters = {k: v for k, v in filters.dict().items() if v is not None}
    return service.filter_questions(active_filters)


@router.get("/unique_values_count/{key}", response_model=UniqueValueCountList)
async def get_unique_values_with_counts_route(key: str):
    return service.get_unique_values_with_counts(key)


@router.get("/get_server_data/{title}/{server}")
async def get_server_data(
    title: str, server: Literal["javascript", "python"] = "javascript"
):
    return service.run_server(question_title=title, server_type=server)


@router.get("/get_question_html/{title}")
async def get_question_html(title: str):
    return HTMLResponse(content=service.get_question_html(question_title=title))


@router.get("/get_question_newformat/{title}")
async def get_question_newformat(title: str):
    question_data = json.loads(service.get_question_newformat(title))

    image_path = Path(f"local_questions/{title}/clientFilesQuestion/image.png")
    if image_path.exists():
        image_url = f"/local_questions/{title}/clientFilesQuestion/image.png"
    else:
        image_url = None

    question_data["image"] = image_url
    return question_data


@router.get("/get_question_files/{title}")
async def get_question_files(title: str):
    return await service.get_question_files(title)


@router.get("/get_question_file/{title}/{filename}")
async def get_question_file(title: str, filename: str):
    return await service.get_file(title, filename)


class UpdateFile(BaseModel):
    title: str
    filename: str
    newcontent: str


@router.post("/update_file/")
async def update_file(file_update: UpdateFile):
    return service.update_file(
        question_title=file_update.title,
        filename=file_update.filename,
        newcontent=file_update.newcontent,
    )


@router.post("/create_file/")
async def create_file(file: UpdateFile):
    return await service.create_file(
        question_title=file.title,
        filename=file.filename,
    )


@router.post("/upload_file/{question_title}")
async def upload_file(file: UploadFile, question_title: str):
    return await service.upload_question_file(file, question_title)
