# --- Standard Library ---
from typing import Literal, cast

# --- Third-Party ---
from fastapi import APIRouter
from pydantic import BaseModel
from starlette import status

# --- Internal ---
from src.api.service.question_manager import QuestionManagerDependency
from src.api.models import *


router = APIRouter()


@router.get("/startup", status_code=status.HTTP_200_OK)
def startup_connection():
    return {"message": "The API is LIVE!!"}


class Settings(BaseModel):
    """API response model for system storage configuration."""

    storage_type: Literal["cloud", "local"]


@router.get("/settings", response_model=Settings)
async def get_current_settings(qm: QuestionManagerDependency) -> Settings:
    """Return the current storage settings (cloud or local)."""
    return Settings(storage_type=cast(Literal["cloud", "local"], qm.storage_type))
