# Standard library
import asyncio
import json
from pathlib import Path
from typing import List, Union
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


from pathlib import Path
from typing import Union
from uuid import UUID
from fastapi import HTTPException
from starlette import status

# adjust these imports to your project
from src.api.core import settings
from src.api.service import question_crud as qc
from src.api.response_models import SuccessDataResponse
from src.utils import safe_name


async def set_directory(question_id: Union[str, UUID], session) -> SuccessDataResponse:
    """
    Ensure a question has a local directory on disk.

    Behavior:
      - If question.local_path exists on disk, return it (200).
      - Else, create a directory under BASE_PATH / QUESTIONS_DIRNAME using a safe name
        derived from the question title; fall back to "question_<uuid>".
      - If the intended directory name already exists for a different question,
        append "_<uuid>" to avoid overwriting.
      - Persist question.local_path as a *relative path* (e.g. "questions/<name>")
        and return it (201).
    """
    # 1) Fetch question
    question = await qc.get_question_by_id(question_id, session)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {question_id} not found",
        )

    if (
        not settings.BASE_PATH
        or not settings.QUESTIONS_PATH
        or not settings.QUESTIONS_DIRNAME
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"base path, question path or question dirname is not set "},
        )
    # 2) Resolve base dir
    base_dir = Path(str(settings.BASE_PATH)) / str(settings.QUESTIONS_DIRNAME)
    base_dir = base_dir.resolve()

    if not base_dir.exists():
        base_dir.mkdir(parents=True, exist_ok=True)

    # 3) If already set and exists, return early (idempotent)
    if question.local_path:
        existing = Path(str(settings.BASE_PATH)) / question.local_path
        if existing.exists() and existing.is_dir():
            return SuccessDataResponse(
                status=status.HTTP_200_OK,
                detail=f"Path for question {question.id} already exists.",
                data=question.local_path,  # stored as relative path
            )

    # 4) Build a safe directory name
    title = (question.title or "").strip()
    base_name = safe_name(title) if title else f"question_{question.id}"
    target = base_dir / base_name

    # 5) Avoid collisions
    if target.exists() and str(target) != (question.local_path or ""):
        target = base_dir / f"{base_name}_{question.id}"

    # 6) Create directory
    try:
        target.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create directory '{target}': {e}",
        ) from e

    # 7) Compute relative path (always relative to BASE_PATH)
    relative_path = f"{settings.QUESTIONS_DIRNAME}/{target.name}"

    # 8) Persist relative path in the DB
    question.local_path = relative_path
    try:
        session.add(question)
        session.commit()
        session.refresh(question)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating Question {question.id}: {e}",
        ) from e

    return SuccessDataResponse(
        status=status.HTTP_201_CREATED,
        detail=f"Path for question '{question.title or question.id}' created successfully.",
        data=relative_path,
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
        qpath = Path(str(settings.BASE_PATH)) / Path(
            str(question.local_path)
        )  # if question.local_path else None
        if qpath and qpath.exists():
            return SuccessDataResponse(
                status=status.HTTP_200_OK,
                detail="Local Path already set",
                data=str(qpath),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No Question Path Set for {question.title}",
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


def write(
    target: Union[str, Path],
    content: Union[str, dict, list, bytes, bytearray],
    overwrite: bool = True,
) -> Path:
    """
    Write raw content to a target path.

    - Dicts and lists are JSON-encoded.
    - Bytes/bytearray are written in binary mode.
    - Strings are written with Path.write_text.
    - If overwrite is False and the file exists, raise HTTP 409.
    - Returns the Path object of the target.
    """
    target = Path(target)
    filename = target.name

    # Prevent overwrite if disabled
    if not overwrite and target.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"File already exists and cannot overwrite {filename}",
        )

    # Handle dicts/lists → JSON
    if isinstance(content, (dict, list)):
        target.write_text(json.dumps(content, indent=2))
        return target

    # Handle bytes/bytearray
    if isinstance(content, (bytes, bytearray)):
        mode = "wb" if overwrite else "xb"
        with open(target, mode) as f:
            f.write(content)
        return target

    # Fallback: write as string
    target.write_text(str(content))
    return target


async def write_file_to_directory(
    question_id: str | UUID, file_data: FileData, session: SessionDep
):
    """
    Ensure the question directory exists, then write a single file to it.

    Returns a SuccessDataResponse with the written file's absolute path.
    """
    try:
        response = await get_question_directory(
            session,
            question_id,
        )
        print("This is getting the local dir")
        print(response)
        base_dir = Path(str(response.data)).resolve()

        print("This is base dir", base_dir)

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
        response = await get_question_directory(
            session,
            question_id,
        )
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

        file_data: List[FileData] = []
        for f in files:
            fpath = Path(f)
            file_data.append(FileData(filename=fpath.name, content=fpath.read_text()))

        return SuccessFileResponse(
            status=status.HTTP_200_OK,
            detail="Retrieved files",
            files=file_data,
            file_paths=files,
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
                detail=f"filename {filename} does not exist for question {question.title}",
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
        return SuccessFileResponse(
            status=status.HTTP_200_OK,
            detail=f"Updated file content {filename} from {question_id} ",
            files=[FileData(filename=filename, content=new_content)],
            file_paths=[file_path],
        )
    except HTTPException:
        raise
