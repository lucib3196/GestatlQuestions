from fastapi import APIRouter
from starlette import status

from src.api.models import *
from src.api.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/startup", status_code=status.HTTP_200_OK)
def startup_connection():
    return {"message": "The API is LIVE!!"}


@router.get("/settings")
async def get_current_settings():
    """Return the current storage settings (cloud or local)."""
    return {"storage_service": settings.STORAGE_SERVICE}
