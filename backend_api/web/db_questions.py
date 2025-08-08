from backend_api.service import db_question as service
from fastapi import APIRouter, Depends
from backend_api.data.database import get_session
from sqlmodel import Session
from typing import List
from backend_api.model.questions_models import QuestionMetaNew
from fastapi import UploadFile

router = APIRouter(prefix="/db_questions")



