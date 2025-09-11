# --- Standard Library ---
import asyncio
import base64
import json
import mimetypes
from pathlib import Path
from typing import List, Literal, Union
from uuid import UUID

# --- Third-Party ---
from fastapi import HTTPException
from starlette import status

# --- Internal ---
from src.api.core import settings
from src.api.database import SessionDep
from src.api.response_models import (
    FileData,
    SuccessDataResponse,
    SuccessFileResponse,
    SuccessfulResponse,
)
from src.api.service import question_crud as qc
from src.utils import safe_name


IMAGE_MIMETYPES = {"image/png"}


def reconstruct_path(relative_path: str | Path) -> Path:
    return Path(settings.BASE_PATH) / Path(relative_path)


async def set_or_get_directory(
    session, question_id, method: Literal["local", "firebase"] = "local"
):
    try:
        # Try to get existing directory
        response = await get_question_directory(session, question_id)
        if response.status == status.HTTP_200_OK:
            return response
    except HTTPException:
        pass

    # Fallback: create a new directory
    return await set_directory(question_id, session)


async def get_question_directory(
    session: SessionDep, question_id: str | UUID
) -> SuccessFileResponse:
    """
    Get the question's local directory as a SuccessDataResponse.

    Returns:
      - 200 with existing path if question.local_path exists on disk.
      - 200 with data=None if no path is set yet.
      - 400 if required fields (title or QUESTIONS_PATH) are missing.
    """
    try:
        question = await qc.get_question_by_id(question_id, session)

        qpath = reconstruct_path(str(question.local_path))

        if qpath and qpath.exists():
            return SuccessFileResponse(
                status=status.HTTP_200_OK,
                detail="Local Path already set",
                file_paths=[str(question.local_path)],
            )
        elif (not qpath.exists()) and question.local_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question Path Set for {question.title}, but directory may not exist (ie points to nowhere)",
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


async def set_directory(
    question_id: Union[str, UUID],
    session,
    method: Literal["local", "firebase"] = "local",
) -> SuccessFileResponse:
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
    if not settings.QUESTIONS_PATH or not settings.BASE_PATH:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"base path, question path or question dirname is not set "},
        )

    question = await qc.get_question_by_id(question_id, session)

    # Create the path
    abs_path = Path(settings.QUESTIONS_PATH).resolve()
    if not abs_path.exists():
        abs_path.mkdir(parents=True, exist_ok=True)

    title = (question.title or "").strip()
    question_title = safe_name(title) if title else f"question_{question.id}"
    target = abs_path / question_title

    # 5) Avoid collisions
    if target.exists() and str(target) != (question.local_path or ""):
        target = abs_path / f"{question_title}_{question.id}"

    # 6) Create directory
    try:
        target.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create directory '{target}': {e}",
        ) from e

    # 7) Compute relative path (always relative to BASE_PATH)
    ## Should return /question/question_title
    relative_path = f"{settings.QUESTIONS_DIRNAME}/{target.name}"

    # 8) Persist relative path in the DB
    question.local_path = relative_path

    # Refresh the database
    await qc.safe_refresh_question(question, session)

    return SuccessFileResponse(
        status=status.HTTP_201_CREATED,
        detail=f"Path for question '{question.title or question.id}' created successfully.",
        file_paths=[relative_path],
        files=[],
    )


async def write_file(f: FileData, dirname: str | Path, overwrite: bool = True):
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
    target = (Path(dirname) / fname).resolve()

    content = f.content
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File {f.filename} has no content",
        )
    target = write(target, content=content, overwrite=True)
    return SuccessfulResponse(
        status=status.HTTP_200_OK, detail=f"wrote content to {fname}"
    )


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
    - Returns the Path object of the target.Returns the absolute path
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


async def write_files_to_directory(
    question_id: str | UUID, files_data: List[FileData], session: SessionDep
):
    """
    Ensure the question directory exists, then write multiple files to it.

    Returns a SuccessFileResponse with the list of absolute paths for all written files.
    """
    try:
        response = await set_or_get_directory(
            session,
            question_id,
        )
        rel_path = response.filepaths[0]
        abs_path = reconstruct_path(rel_path)

        # Write files to the directory
        result = await asyncio.gather(
            *[write_file(f, abs_path.resolve()) for f in files_data]
        )
        for r in result:
            assert r.status == 200

        return SuccessFileResponse(
            status=status.HTTP_200_OK,
            detail="Wrote files to directory Correctly",
            file_paths=[str(Path(rel_path) / f.filename) for f in files_data],
            files=files_data,
        )
    except HTTPException:
        raise


async def get_files_from_directory(
    question_id: str | UUID, session: SessionDep, skip_images: bool = True
):
    """
    List all files (not directories) within the question's local directory.

    Returns a SuccessFileResponse with a list of absolute file paths.
    """
    try:
        question = await qc.get_question_by_id(question_id, session)
        response = await get_question_directory(session, question.id)
        question_path = reconstruct_path(response.filepaths[0])

        files = [str(f) for f in question_path.iterdir() if f.is_file]

        file_data: List[FileData] = []
        for f in files:
            fpath = Path(f)
            mime_type = mimetypes.guess_type(fpath.name)
            if mime_type[0] and (mime_type[0] not in IMAGE_MIMETYPES):
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            else:
                if skip_images:
                    content = "Some Image"
                else:
                    with open(fpath, "rb") as bin_file:
                        content = base64.b64encode(bin_file.read()).decode("utf-8")
            file_data.append(FileData(filename=fpath.name, content=content))
        return SuccessFileResponse(
            status=status.HTTP_200_OK,
            detail="Retrieved files",
            files=file_data,
            file_paths=[Path(f).relative_to(settings.BASE_PATH) for f in files],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


async def get_file_path_abs(
    question_id: str | UUID, filename: str, session: SessionDep
):
    """
    Resolve and validate the absolute path to a specific file for a question.

    Returns a SuccessDataResponse with the absolute file path if found,
    otherwise raises HTTP 400.
    """
    try:
        question = await qc.get_question_by_id(question_id, session)
        response = await get_question_directory(session, question.id)

        question_path = reconstruct_path(response.filepaths[0])
        filepath = question_path / safe_name(filename)
        file_exist = filepath.is_file()
        if file_exist:
            return SuccessFileResponse(
                status=status.HTTP_200_OK,
                detail=f"File Found {filename}",
                file_paths=[filepath],
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
        response = await get_file_path_abs(question_id, filename, session=session)
        filepath = response.filepaths[0]
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
        r = await get_file_path_abs(question_id, filename, session)
        # Delete file
        Path(str(r.filepaths[0])).unlink(missing_ok=True)
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
        r = await get_file_path_abs(question_id, filename, session)
        file_path = Path(r.filepaths[0])
        file_path = write(file_path, content=new_content, overwrite=True)
        return SuccessFileResponse(
            status=status.HTTP_200_OK,
            detail=f"Updated file content {filename} from {question_id} ",
            files=[FileData(filename=filename, content=new_content)],
            file_paths=[file_path],
        )
    except HTTPException:
        raise
