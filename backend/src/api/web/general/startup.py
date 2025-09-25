# --- Standard Library ---

# --- Third-Party ---
from fastapi import APIRouter
from starlette import status

# --- Internal ---
from src.api.response_models import *


router = APIRouter()


@router.get("/startup", status_code=status.HTTP_200_OK)
def startup_connection():
    return {"message": "The API is LIVE!!"}
