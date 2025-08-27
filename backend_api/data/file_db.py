# Standard library
import json
from typing import Sequence, Union
from uuid import UUID

# Third-party
from sqlmodel import select

# Local
from backend_api.data.database import SessionDep
from backend_api.model.file_model import File
from backend_api.utils import get_uuid


def add_file(file_obj: File, session: SessionDep) -> File:
    """Add a new file to the database and return the persisted object."""
    if isinstance(file_obj.content, dict):
        file_obj.content = json.dumps(file_obj.content)

    session.add(file_obj)
    session.commit()
    session.refresh(file_obj)
    return file_obj


def get_file_by_id(file_id: Union[str, UUID], session: SessionDep) -> File:
    """Look up a File by its ID. Raises ValueError if not found or invalid."""
    try:
        file_uuid = get_uuid(file_id)
    except ValueError:
        raise ValueError(f"Invalid file id: {file_id}")

    result = session.exec(select(File).where(File.id == file_uuid)).first()
    if not result:
        raise ValueError(f"File not found: {file_id}")
    return result


def list_files(session: SessionDep) -> Sequence[File]:
    """Return all files in the database."""
    return session.exec(select(File)).all()


def delete_file(session: SessionDep, file_id: Union[str, UUID]) -> None:
    """Delete a file from the database by ID. Raises ValueError if missing."""
    file_obj = get_file_by_id(file_id=file_id, session=session)
    if not file_obj:
        raise ValueError("File not in db")

    session.delete(file_obj)
    session.commit()
    session.flush()


def edit_file_content(
    file_id: Union[str, UUID], new_content: Union[str, dict], session: SessionDep
) -> File:
    """
    Update the content of a File by its ID. Accepts str or dict content.
    Raises ValueError if the file doesn't exist or update fails.
    """
    try:
        file_obj = get_file_by_id(file_id, session)

        if isinstance(new_content, dict):
            new_content = json.dumps(new_content)

        file_obj.content = new_content
        session.commit()
        session.refresh(file_obj)
        return file_obj

    except ValueError:
        # bubble up cleanly if get_file_by_id already raised
        raise
    except Exception as e:
        raise ValueError(f"Could not update file content: {str(e)}")
