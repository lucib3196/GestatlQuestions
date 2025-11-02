# Standard library
import tempfile
from pathlib import Path
from typing import Literal
from uuid import UUID

# Third-party libraries
from fastapi import APIRouter, HTTPException
from starlette import status

# Local application imports
from src.api.core import logger
from src.api.database import SessionDep
from src.api.service.question_manager import QuestionManagerDependency
from src.code_runner.models import CodeRunException, CodeRunResponse, QuizData
from src.code_runner.runtime_switcher import run_generate


router = APIRouter(prefix="/question_running", tags=["dev", "code_running"])

MAPPING_DB = {"python": "server.py", "javascript": "server.js"}
MAPPPING_FILENAME = {"python": "server.py", "javascript": "server.js"}


@router.post("/run_server/{qid}/{server_language}", response_model=QuizData)
async def run_server(
    qid: str | UUID,
    server_language: Literal["python", "javascript"],
    session: SessionDep,
    qm: QuestionManagerDependency,
) -> QuizData:
    # Mapping from language to filename
    
    logger.debug(f"Attemping to get question {qid}")
    try:
        server_file = MAPPPING_FILENAME[server_language]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language: {server_language}",
        )

    # Validate that file exists for the question
    try:
        files = await qm.get_all_files(qid, session)
        if server_file not in files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question does not contain file {server_file}",
            )
    except HTTPException:
        raise  # keep original
    except Exception as e:
        logger.exception("Error while fetching question files")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error accessing question files",
        ) from e

    try:
        file_content = await qm.read_file(qid, session, server_file)
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {server_file} is empty or unreadable.",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error while reading question file")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file {server_file}",
        ) from e

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / server_file
            tmp_path.write_bytes(file_content)
            run_response: CodeRunResponse = run_generate(
                tmp_path, server_language, isTesting=False
            )

    except CodeRunException:
        raise
    except Exception as e:
        logger.exception("Error while running server file")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running {server_language} file {server_file}: {str(e)}",
        ) from e

    # Finally return the quiz response
    try:
        data = run_response.quiz_response
        assert data
        return data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Code ran successfully but quiz data is None",
        )
