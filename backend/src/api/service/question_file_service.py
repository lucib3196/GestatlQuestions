from uuid import UUID
from typing import Union

from fastapi import HTTPException
from starlette import status
from sqlmodel import select

from api.utils import get_uuid, SuccessFileResponse
from api.data.database import SessionDep
from api.models.file_model import File
from api.data import file_db
from api.data import question_db


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


def delete_file(file_id: UUID | str, session: SessionDep):
    try:
        file_db.delete_file(session, file_id)
        return {"detail": f"File {file_id} deleted"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


def delete_file_by_question_id(
    question_id: Union[str, UUID], filename: str, session: SessionDep
):
    try:
        question = question_db.get_question_by_id(question_id, session)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question is not valid cannot add file",
            )
        qfile = session.exec(select(File).where(filename == filename)).first()
        if not qfile:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail=f"File not found {filename}",
            )
        delete_file(file_id=qfile.id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
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
        question = question_db.get_question_by_id(question_id, session)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question is not valid",
            )
        results = session.exec(
            select(File).where(File.question_id == question_uuid)
        ).all()
        return SuccessFileResponse(
            status=status.HTTP_200_OK,
            detail=f"Got all files for question {question.title}",
            file_obj=list(results) or [],
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Question ID is not valid"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
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
