# Stdlib
import asyncio
from pathlib import Path
from typing import List, Literal
from uuid import UUID

# Internal
from src.api.core import logger
from src.api.database import SessionDep
from src.api.models import Question
from src.api.response_models import FileData
from src.api.service.crud import question_crud as qc
from src.api.service.storage import StorageService
from src.utils import safe_dir_name


class QuestionManager:
    """Manage creation, retrieval, and file operations for questions."""

    def __init__(
        self, storage_service: StorageService, storage_type: Literal["local", "cloud"]
    ):
        """Initialize with a storage backend and storage type."""
        self.storage = storage_service
        self.storage_type = storage_type

    # ---------------------------
    # Question Lifecycle
    # ---------------------------
    async def create_question(
        self, question: Question | dict, session: SessionDep, existing: bool = False
    ) -> Question:
        """Create a new question in DB and storage."""
        try:
            q = await qc.create_question(question, session)
        except Exception as e:
            logger.error("Failed to create question in DB: %s", e)
            raise

        try:
            qname = safe_dir_name((q.title or "").strip())
            logger.info("Created question successfully %s", q.title)

            if not qname:
                logger.error("Question title is None")
                raise ValueError("Question title cannot be None")

            if self.storage.does_directory_exist(qname) and not self.get_question_path(
                q
            ):
                logger.info("Question title duplicate found creating a new title")
                qname = f"{qname}_{q.id}"

            self.storage.create_directory(qname)
            self.set_question_path(q, qname)
            return q
        except Exception as e:
            logger.error(
                "Failed to set up storage for question %s: %s",
                getattr(q, "title", None),
                e,
            )
            raise

    async def update_question(
        self, question_id: str | UUID, session: SessionDep, **kwargs
    ):
        """Update question metadata in the DB."""
        try:
            return await qc.edit_question_meta(question_id, session, **kwargs)
        except Exception as e:
            logger.error(f"Failed to update question {str(e)}")
            raise

    async def get_question(self, question_id: str | UUID, session: SessionDep):
        """Retrieve a question by ID."""
        try:
            return await qc.get_question_by_id(question_id, session)
        except Exception as e:
            logger.error("Failed to retrieve question %s: %s", question_id, e)
            raise

    async def get_question_identifier(
        self, question_id: str | UUID, session: SessionDep
    ):
        """Get the storage identifier (folder/blob name) for a question."""
        q = await self.get_question(question_id, session)
        if q is None:
            logger.error("Failed to get a question")
            raise ValueError("Question is None")

        try:
            qpath = self.get_question_path(q)
            return Path(qpath).name if qpath else None
        except Exception as e:
            logger.error(
                "Error while extracting identifier for question %s: %s", question_id, e
            )
            raise

    # ---------------------------
    # File Operations
    # ---------------------------
    async def save_file_to_question(
        self,
        question_id: str | UUID,
        session: SessionDep,
        file: FileData,
        overwrite: bool = False,
    ) -> bool:
        """Save a single file to a question directory."""
        try:
            await self.get_question(question_id, session)
            identifier = await self.get_question_identifier(question_id, session)
            if not identifier:
                raise ValueError("Could not resolve question identifier")

            self.storage.save_file(identifier, file.filename, file.content, overwrite)
            logger.info(f"Wrote file {file.filename} for question {question_id}")
            return True
        except Exception as e:
            logger.error(
                "Failed saving file %s for question %s: %s",
                file.filename,
                question_id,
                e,
            )
            raise

    async def save_files_to_question(
        self,
        question_id: str | UUID,
        session: SessionDep,
        files: List[FileData],
        overwrite: bool = False,
    ) -> bool:
        """Save multiple files to a question directory."""
        try:
            await asyncio.gather(
                *[
                    self.save_file_to_question(question_id, session, f, overwrite)
                    for f in files
                ]
            )
            return True
        except Exception as e:
            logger.error("Failed to save files to question %s: %s", question_id, e)
            raise

    async def get_file(
        self, question_id: str | UUID, session: SessionDep, filename: str
    ) -> bytes | None:
        """Retrieve a file from a question directory."""
        try:
            qidentifier = await self.get_question_identifier(question_id, session)
            if not qidentifier:
                raise ValueError("Could not resolve question identifier")
            return self.storage.get_file(qidentifier, filename)
        except Exception as e:
            logger.error("Failed to get file %s for question %s", filename, question_id)
            raise

    async def get_all_files(self, question_id: str | UUID, session: SessionDep):
        """Retrieve all file names for a given question."""
        try:
            qidentifier = await self.get_question_identifier(question_id, session)
            if not qidentifier:
                raise ValueError("Could not resolve question identifier")
            return self.storage.get_files_names(qidentifier)
        except Exception as e:
            logger.error("Failed to get files for question %s", question_id)
            raise

    # ---------------------------
    # Deletion
    # ---------------------------
    async def delete_question(self, question_id: str | UUID, session: SessionDep):
        """Delete a question and all its files."""
        try:
            qidentifier = await self.get_question_identifier(question_id, session)
            if not qidentifier:
                raise ValueError("Could not resolve question identifier")
            await qc.delete_question_by_id(question_id, session)
            self.storage.delete_all(qidentifier)
        except Exception as e:
            logger.error("Failed to delete question %s: %s", question_id, e)
            raise

    async def delete_question_file(
        self, question_id: str | UUID, session: SessionDep, filename: str
    ):
        """Delete a single file from a question."""
        try:
            qidentifier = await self.get_question_identifier(question_id, session)
            if not qidentifier:
                raise ValueError("Could not resolve question identifier")
            self.storage.delete_file(qidentifier, filename)
        except Exception as e:
            logger.error("Failed to delete file %s %s: %s", question_id, filename, e)
            raise

    # ---------------------------
    # Helpers
    # ---------------------------
    def get_question_path(self, q: Question):
        """Return the stored path (local or cloud) for a question."""
        try:
            if self.storage_type == "local":
                return q.local_path
            elif self.storage_type == "cloud":
                return q.blob_name
        except Exception as e:
            logger.error(
                "Failed to get question path for %s: %s", getattr(q, "title", None), e
            )
            raise

    def set_question_path(self, q: Question, qname: str):
        """Assign storage path to a question object."""
        try:
            path = self.storage.get_directory(qname).as_posix()
            if self.storage_type == "local":
                q.local_path = str(path)
            elif self.storage_type == "cloud":
                q.blob_name = str(path)
        except Exception as e:
            logger.error(
                "Failed to set question path for %s: %s", getattr(q, "title", None), e
            )
            raise

    def get_basename(self) -> str | Path:
        """Return the base directory/bucket name from storage."""
        try:
            return self.storage.get_basename()
        except Exception as e:
            logger.error("Failed to get basename from storage: %s", e)
            raise
