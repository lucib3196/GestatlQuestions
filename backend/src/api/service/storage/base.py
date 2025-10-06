from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Optional, List
from google.cloud.storage.blob import Blob
import io

class StorageService:
    """
    Base storage interface for managing files and directories.

    Subclasses should override the methods they need, depending on the
    underlying storage mechanism (local, cloud, hybrid).
    """

    def get_basename(self) -> Union[str, Path]:
        """Return the base path or bucket name."""
        raise NotImplementedError("get_basename must be implemented by subclass")

    def get_directory(self, identifier: str) -> Path:
        """Return a directory path for the given identifier."""
        raise NotImplementedError("get_directory must be implemented by subclass")

    def create_directory(self, identifier: str) -> Union[Path, Blob]:
        """Create a directory or blob container for the given identifier."""
        raise NotImplementedError("create_directory must be implemented by subclass")

    def does_directory_exist(self, identifier: str) -> bool:
        """Check whether a directory exists for the given identifier."""
        raise NotImplementedError(
            "does_directory_exist must be implemented by subclass"
        )

    def get_filepath(self, identifier: str, filename: str) -> Path:
        """Get the full path to a file inside the given identifier directory."""
        raise NotImplementedError("get_filepath must be implemented by subclass")

    def save_file(
        self,
        identifier: str,
        filename: str,
        content: Union[str, dict, list, bytes, bytearray],
        overwrite: bool = True,
    ) -> Path:
        """Save a file with the given content under the specified identifier."""
        raise NotImplementedError("save_file must be implemented by subclass")

    def get_file(self, identifier: str, filename: str) -> Optional[bytes]:
        """Retrieve a file's contents by identifier and filename."""
        raise NotImplementedError("get_file must be implemented by subclass")

    def get_files_names(self, identifier: str) -> List[str]:
        """List all file names under the given identifier directory."""
        raise NotImplementedError("get_files_names must be implemented by subclass")

    def delete_file(self, identifier: str, filename: str) -> None:
        """Delete a specific file under the given identifier."""
        raise NotImplementedError("delete_file must be implemented by subclass")

    def delete_all(self, identifier: str) -> None:
        """Delete all files for the given identifier."""
        raise NotImplementedError("delete_all must be implemented by subclass")

    def hard_delete(self) -> None:
        """Remove the entire storage base (irreversible)."""
        raise NotImplementedError("hard_delete must be implemented by subclass")

    async def download_question(self, identifier: str) -> bytes | io.BytesIO:
        """Download a single question file by identifier."""
        raise NotImplementedError("download_question must be implemented by subclass")

    async def download_questions(self, identifiers: List[str]) -> None:
        """Download multiple question files by their identifiers."""
        raise NotImplementedError("download_questions must be implemented by subclass")
