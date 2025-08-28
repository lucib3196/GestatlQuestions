from uuid import UUID
from typing import Union, Optional, List, Annotated

from fastapi import HTTPException
from starlette import status
from sqlmodel import select
from pydantic import BaseModel

from backend_api.utils import get_uuid, SuccessFileResponse
from backend_api.data.database import SessionDep
from backend_api.model.file_model import File
from backend_api.data import file_db
from backend_api.data import question_db
from pydantic import BaseModel, field_validator


def get_question_file(
    question_id: Union[str, UUID], filename: str, session: SessionDep
) -> SuccessFileResponse:

    try:
        question_uuid = get_uuid(question_id)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Question ID is not valid"
        )

    question = question_db.get_question_by_id(
        question_id=question_uuid, session=session
    )
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not Found"
        )

    results = session.exec(
        select(File)
        .where(File.question_id == question_uuid)
        .where(File.filename == filename)
    ).first()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No File {filename} for Question",
        )
    return SuccessFileResponse(
        status=status.HTTP_200_OK,
        detail=f"{filename} in question found",
        file_obj=[results],
    )


def add_file_to_question(
    question_id: Union[str, UUID],
    filename: str,
    content: Union[dict, str],
    session: SessionDep,
) -> SuccessFileResponse:

    question = question_db.get_question_by_id(question_id, session)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is not valid cannot add file",
        )
    new_file = File(filename=filename, content=content, question_id=question.id)
    file_obj = file_db.add_file(new_file, session)
    return SuccessFileResponse(
        status=status.HTTP_201_CREATED,
        detail=f"File {filename} added to question {question.title}",
        file_obj=[file_obj],
    )


def get_all_files(
    question_id: Union[str, UUID], session: SessionDep
) -> SuccessFileResponse:

    try:
        question_uuid = get_uuid(question_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Question ID is not valid"
        )
    question = question_db.get_question_by_id(question_id, session)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question is not valid",
        )

    results = session.exec(select(File).where(File.question_id == question_uuid)).all()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Files for Question"
        )
    return SuccessFileResponse(
        status=status.HTTP_200_OK,
        detail=f"Got all files for question {question.title}",
        file_obj=list(results),
    )


def update_question_file(
    question_id: Union[str, UUID],
    filename: str,
    new_content: Union[str, dict],
    session: SessionDep,
) -> SuccessFileResponse:
    response = get_question_file(question_id, filename, session)
    file_obj = file_db.update_file_content(response.file_obj[0], new_content, session)
    return SuccessFileResponse(
        status=status.HTTP_200_OK,
        detail=f"Updated file {filename} succesfully",
        file_obj=[file_obj],
    )
