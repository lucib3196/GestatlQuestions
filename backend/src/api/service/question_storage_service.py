# Standard library
import asyncio
import json
from pathlib import Path
from typing import List
from uuid import UUID

# Third-party
from fastapi import HTTPException
from starlette import status

# Local
from src.api.core import settings
from src.api.database import SessionDep
from src.api.response_models import (
    FileData,
    SuccessDataResponse,
    SuccessFileResponse,
)
from src.api.service import question_crud as qc
from src.utils import safe_name


async def set_directory(question_id: str | UUID, session: SessionDep):
    """
    Ensure a question has a local directory on disk.

    If a directory is already set/exists, returns that path.
    Otherwise, creates a directory under settings.QUESTIONS_PATH using a safe
    version of the question title (falling back to title_id if needed), updates
    the question.local_path, and returns the created path in a SuccessDataResponse.
    """
    try:
        question = await qc.get_question_by_id(question_id, session)
        response = await get_question_directory(session, question.id)
        assert question.title
        assert settings.QUESTIONS_PATH

        if response.data:
            return response
        else:
            path = Path(settings.QUESTIONS_PATH) / safe_name(question.title)
            if path.exists() and (question.local_path is None):
                # Handle Cases where questions have the same name prevent
                # Previous data from getting overwritten
                path = Path(settings.QUESTIONS_PATH) / safe_name(
                    f"{question.title}_{question.id}"
                )
            path = path.resolve()
            # Create the path
            path.mkdir(parents=True, exist_ok=True)
            question.local_path = str(path.resolve())

            session.add(question)
            session.commit()
            session.refresh(question)

            return SuccessDataResponse(
                status=status.HTTP_201_CREATED,
                detail=f"Path for question {question.title} created successfully",
                data=question.local_path,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not set directory {e}",
        )


async def get_question_directory(session: SessionDep, question_id: str | UUID):
    """
    Get the question's local directory as a SuccessDataResponse.

    Returns:
      - 200 with existing path if question.local_path exists on disk.
      - 200 with data=None if no path is set yet.
      - 400 if required fields (title or QUESTIONS_PATH) are missing.
    """
    try:
        question = await qc.get_question_by_id(question_id, session)
        if not (question.title and settings.QUESTIONS_PATH):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question missing required fields (title or QUESTIONS_PATH).",
            )
        qpath = Path(str(question.local_path)) if question.local_path else None
        if qpath and qpath.exists():
            return SuccessDataResponse(
                status=status.HTTP_200_OK,
                detail="Local Path already set",
                data=str(qpath),
            )
        else:
            return SuccessDataResponse(
                status=status.HTTP_200_OK,
                detail=f"No Question Path Set for {question.title}",
                data=None,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not set directory {e}",
        )


async def write_file(f: FileData, base_dir: str | Path, overwrite: bool = True):
    """
    Write a single FileData into base_dir.

    - Validates filename and non-empty content.
    - Normalizes filename via safe_name.
    - Delegates to write() for actual disk I/O.
    - Returns the absolute path string to the written file.
    """
    if not getattr(f, "filename", None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing a filename for the file",
        )

    fname = safe_name(f.filename)
    target = (Path(base_dir) / fname).resolve()

    content = f.content
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {f.filename} has no content",
        )
    target = write(target, content=content, overwrite=True)
    return str(target)


def write(target: str | Path, content: str | dict | bytes, overwrite: bool = True):
    """
    Write raw content to a target path.

    - Dicts are JSON-encoded.
    - Bytes are written in binary mode.
    - Strings are written with Path.write_text.
    - If overwrite is False and the file exists, raise HTTP 409.
    - Returns the Path object of the target.
    """
    target = Path(target)
    filename = str(target).split("/").pop()
    # Handle cases of the content
    if isinstance(content, dict):
        content = json.dumps(content)
    if isinstance(content, (bytes, bytearray)):
        if not overwrite and target.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"File already exist and cannot overwrite {filename}",
            )
        mode = "wb" if overwrite else "xb"
        with open(target, mode) as fn:
            fn.write(content)
    else:
        s = str(content)
        if not overwrite and target.exists():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"File already exist and cannot overwrite {filename}",
            )
        mode = "wb" if overwrite else "xb"
        target.write_text(content)  # type: ignore
    return target


async def write_file_to_directory(
    question_id: str | UUID, file_data: FileData, session: SessionDep
):
    """
    Ensure the question directory exists, then write a single file to it.

    Returns a SuccessDataResponse with the written file's absolute path.
    """
    try:
        response = await set_directory(question_id, session)
        base_dir = Path(str(response.data)).resolve()

        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided.",
            )
        result = await write_file(file_data, base_dir, overwrite=True)
        return SuccessDataResponse(
            status=status.HTTP_200_OK,
            detail="Wrote files to directory Correctly",
            data=result,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding files {e}",
        )


async def write_files_to_directory(
    question_id: str | UUID, files_data: List[FileData], session: SessionDep
):
    """
    Ensure the question directory exists, then write multiple files to it.

    Returns a SuccessFileResponse with the list of absolute paths for all written files.
    """
    try:
        response = await set_directory(question_id, session)
        base_dir = Path(str(response.data)).resolve()

        results = await asyncio.gather(*[write_file(f, base_dir) for f in files_data])
        return SuccessFileResponse(
            status=status.HTTP_200_OK,
            detail="Wrote files to directory Correctly",
            files=results,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding files {e}",
        )


async def get_files_from_directory(question_id: str | UUID, session: SessionDep):
    """
    List all files (not directories) within the question's local directory.

    Returns a SuccessFileResponse with a list of absolute file paths.
    """
    try:
        question = await qc.get_question_by_id(question_id, session)
        response = await get_question_directory(session, question.id)
        assert question.title
        assert settings.QUESTIONS_PATH

        question_path = Path(str(response.data)).resolve()
        files = [str(f) for f in question_path.iterdir() if f.is_file]

        return SuccessFileResponse(
            status=status.HTTP_200_OK, detail="Retrieved files", files=files
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def get_file_path(question_id: str | UUID, filename: str, session: SessionDep):
    """
    Resolve and validate the absolute path to a specific file for a question.

    Returns a SuccessDataResponse with the absolute file path if found,
    otherwise raises HTTP 400.
    """
    try:
        question = await qc.get_question_by_id(question_id, session)
        response = await get_question_directory(session, question.id)
        assert question.title
        assert settings.QUESTIONS_PATH

        question_path = Path(str(response.data)).resolve()
        filepath = question_path / safe_name(filename)
        file_exist = filepath.is_file()
        if file_exist:
            return SuccessDataResponse(
                status=status.HTTP_200_OK,
                detail=f"File Found {filename}",
                data=str(filepath),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"filename f{filename} does not exist for question {question.title}",
            )
    except HTTPException:
        raise


async def get_file_content(question_id: str | UUID, filename: str, session: SessionDep):
    """
    Read and return the content of a specific file for a question.

    Returns a SuccessFileResponse containing a single FileData with the file content.
    """
    try:
        response = await get_file_path(question_id, filename, session=session)
        filepath = response.data
        return SuccessFileResponse(
            files=[
                FileData(filename=filename, content=Path(str(filepath)).read_text())
            ],
            status=status.HTTP_200_OK,
            detail="",
        )
    except HTTPException:
        raise


async def delete_file(question_id: str | UUID, filename: str, session: SessionDep):
    """
    Delete a specific file for a question if it exists.

    Returns a SuccessDataResponse confirming deletion (idempotent with missing_ok=True).
    """
    try:
        r = await get_file_path(question_id, filename, session)

        # Delete file
        Path(str(r.data)).unlink(missing_ok=True)
        return SuccessDataResponse(
            status=status.HTTP_200_OK,
            detail=f"Deleted file {filename} from {question_id} ",
            data=None,
        )
    except HTTPException:
        raise


async def update_file_content(
    question_id: str | UUID,
    filename: str,
    new_content: str | dict | bytes,
    session: SessionDep,
):
    """
    Overwrite the content of an existing file for a question.

    Uses write() to replace content atomically (respecting overwrite=True)
    and returns the absolute path of the updated file.
    """
    try:
        r = await get_file_path(question_id, filename, session)
        file_path = Path(str(r.data))
        file_path = write(file_path, content=new_content, overwrite=True)
        return SuccessDataResponse(
            status=status.HTTP_200_OK,
            detail=f"Updated file content {filename} from {question_id} ",
            data=str(file_path),
        )
    except HTTPException:
        raise


# def get_question_file(
#     question_id: Union[str, UUID], filename: str, session: SessionDep
# ) -> SuccessFileResponse:

#     try:
#         question_uuid = get_uuid(question_id)

#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Question ID is not valid"
#         )

#     question = question_db.get_question_by_id(
#         question_id=question_uuid, session=session
#     )
#     if not question:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Question not Found"
#         )

#     results = session.exec(
#         select(File)
#         .where(File.question_id == question_uuid)
#         .where(File.filename == filename)
#     ).first()
#     if not results:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No File {filename} for Question",
#         )
#     return SuccessFileResponse(
#         status=status.HTTP_200_OK,
#         detail=f"{filename} in question found",
#         file_obj=[results],
#     )


# def delete_file(file_id: UUID | str, session: SessionDep):
#     try:
#         file_db.delete_file(session, file_id)
#         return {"detail": f"File {file_id} deleted"}
#     except ValueError as e:
#         raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=str(e))
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )


# def delete_file_by_question_id(
#     question_id: Union[str, UUID], filename: str, session: SessionDep
# ):
#     try:
#         question = question_db.get_question_by_id(question_id, session)
#         if not question:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Question is not valid cannot add file",
#             )
#         qfile = session.exec(select(File).where(filename == filename)).first()
#         if not qfile:
#             raise HTTPException(
#                 status_code=status.HTTP_204_NO_CONTENT,
#                 detail=f"File not found {filename}",
#             )
#         delete_file(file_id=qfile.id, session=session)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )


# def add_file_to_question(
#     question_id: Union[str, UUID],
#     filename: str,
#     content: Union[dict, str],
#     session: SessionDep,
# ) -> SuccessFileResponse:

#     question = question_db.get_question_by_id(question_id, session)
#     if not question:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Question is not valid cannot add file",
#         )
#     new_file = File(filename=filename, content=content, question_id=question.id)
#     file_obj = file_db.add_file(new_file, session)
#     return SuccessFileResponse(
#         status=status.HTTP_201_CREATED,
#         detail=f"File {filename} added to question {question.title}",
#         file_obj=[file_obj],
#     )


# def get_all_files(
#     question_id: Union[str, UUID], session: SessionDep
# ) -> SuccessFileResponse:

#     try:
#         question_uuid = get_uuid(question_id)
#         question = question_db.get_question_by_id(question_id, session)
#         if not question:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Question is not valid",
#             )
#         results = session.exec(
#             select(File).where(File.question_id == question_uuid)
#         ).all()
#         return SuccessFileResponse(
#             status=status.HTTP_200_OK,
#             detail=f"Got all files for question {question.title}",
#             file_obj=list(results) or [],
#         )
#     except ValueError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail="Question ID is not valid"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )


# def update_question_file(
#     question_id: Union[str, UUID],
#     filename: str,
#     new_content: Union[str, dict],
#     session: SessionDep,
# ) -> SuccessFileResponse:
#     response = get_question_file(question_id, filename, session)
#     file_obj = file_db.update_file_content(response.file_obj[0], new_content, session)
#     return SuccessFileResponse(
#         status=status.HTTP_200_OK,
#         detail=f"Updated file {filename} succesfully",
#         file_obj=[file_obj],
#     )
