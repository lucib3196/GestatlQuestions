from backend_api.service import db_question as service
from fastapi import APIRouter, Depends
from backend_api.data.database import get_session
from sqlmodel import Session
from typing import List
from backend_api.model.questions_models import QuestionMetaNew
from fastapi import UploadFile
from backend_api.model.questions_models import Question, QuestionDict
from uuid import UUID
from backend_api.data.database import SessionDep
from fastapi import HTTPException


router = APIRouter(prefix="/db_questions")


@router.post("get_all_questions/{offset}/{limit}", response_model=List[Question])
async def get_all_questions(offset: int, limit: int, session=Depends(get_session)):
    return await service.get_all_questions(session, offset=offset, limit=limit)


@router.post("/filter_question", response_model=List[Question])
async def get_filtered_questions(qfilter: QuestionDict, session=Depends(get_session)):

    return await service.filter_questions(session, qfilter)


@router.post("/delete_question")
async def delete_question(question_id: str, session: SessionDep):
    # convert
    try:
        question_uuid = UUID(question_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    return await service.delete_question(question_uuid, session)
