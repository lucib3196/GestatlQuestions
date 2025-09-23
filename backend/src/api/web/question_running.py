from uuid import UUID
from typing import Union, Literal
from starlette import status
from fastapi import APIRouter, HTTPException
from src.api.database import SessionDep
from src.api.service.code_running import question_running_service

router = APIRouter(prefix="/question_running")


@router.post("/run_server/{qid}/{server_language}")
async def run_server(
    qid: Union[str, UUID],
    server_language: Literal["javascript", "python"],
    session: SessionDep,
):
    try:
        return await question_running_service.run_server(
            question_id=qid, code_language=server_language, session=session
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unknown Error {e}",
        )
