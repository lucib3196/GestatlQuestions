# Standard library
import json
from typing import Union, Literal
from uuid import UUID
from pathlib import Path

# Third-party
from fastapi import HTTPException
from starlette import status
import tempfile

# Local
from backend_api.core.logging import logger
from backend_api.data.database import SessionDep
from code_runner.run_server import run_generate
from backend_api.utils import get_uuid
from backend_api.service import question_file_service
from backend_api.service.question_file_service import SuccessFileResponse


async def run_server(
    question_id: Union[str, UUID],
    code_language: Literal["python", "javascript"],
    session: SessionDep,
):
    mapping_db = {"python": "server.py", "javascript": "server.js"}
    mapping_filename = {"python": "server.py", "javascript": "server.js"}

    if (isinstance, str):
        question_id = get_uuid(question_id)

    # Validate language
    if code_language not in mapping_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported code language"
        )

    try:
        response: SuccessFileResponse = question_file_service.get_question_file(
            question_id, mapping_db[code_language], session
        )
    except HTTPException:
        raise

    server_file = response.file_obj[0]
    server_content = server_file.content

    if isinstance(server_content, (dict, list)):
        try:
            server_content = json.dumps(server_content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to serialize server content: {e}",
            )
    elif not isinstance(server_content, str):

        server_content = str(server_content)
    # Write to a temp file and execute

    # Try to run the file
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / mapping_filename[code_language]
            file_path.write_text(server_content, encoding="utf-8")
            logger.debug("Executing server code at %s", file_path)
            output = run_generate(str(file_path), isTesting=False)
            return output
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Execution error: {e}",
        )
