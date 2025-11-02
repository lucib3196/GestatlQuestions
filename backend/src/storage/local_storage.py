# --- Standard Library ---
import json
from pathlib import Path
from typing import List, Union
import shutil
import os

# --- Internal ---
from .base import StorageService
from src.storage.directory_service import DirectoryService
from src.api.core import logger
from src.api.service.file_handler import FileService
from src.utils import safe_dir_name


class LocalStorageService(StorageService):
    """
    Local storage implementation of `StorageService`.

    Handles file operations (create, save, delete, download) on the local filesystem.
    Uses `DirectoryService` for directory management and `FileService` for file zipping
    and download operations.
    """

    # -------------------------------------------------------------------------
    # Initialization / Lifecycle
    # -------------------------------------------------------------------------

    def __init__(self, root: str | Path):
        """
        Initialize the local storage service with a base directory.

        Args:
            root: Path or string specifying the root storage directory.
        """
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

        logger.debug(
            "Initialized the storage, questions will be stored at %s", self.root
        )

        download_path = self.root / "downloads"
        self.file_service = FileService(download_path)

    # -------------------------------------------------------------------------
    # Base path operations
    # -------------------------------------------------------------------------

    def get_base_path(self) -> Path:
        """
        Return the absolute path to the base directory for local storage.

        Returns:
            Path: The resolved base directory path.
        """
        return self.root

    def get_base_name(self) -> str:
        """
        Return the name of the base directory.

        Returns:
            str: The base directory name (e.g., "questions").
        """
        return str(self.root.name)

    def get_storage_path(self, identifier: str) -> Path:
        """
        Build the absolute path for a resource based on its identifier.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            Path: Path to the resource directory.
        """
        return self.root / safe_dir_name(identifier)

    def create_storage_path(self, identifier: str) -> Path:
        """
        Create a directory for the given identifier if it does not exist.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            Path: Path to the created directory.
        """
        storage = self.get_storage_path(identifier)
        storage.mkdir(parents=True, exist_ok=True)
        return storage

    def get_relative_storage_path(self, identifier):
        """
        Return the relative path of a storage directory from the base root.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            Path: Relative path to the storage directory.
        """
        return self.get_storage_path(identifier).relative_to(self.root.parent)

    def does_storage_path_exist(self, identifier: str) -> bool:
        """
        Check if a directory exists for a given identifier.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        return self.get_storage_path(identifier).exists()

    # -------------------------------------------------------------------------
    # File access and management
    # -------------------------------------------------------------------------

    def get_filepath(self, identifier: str, filename: str) -> Path:
        """
        Build the absolute file path for a given identifier and filename.

        Args:
            identifier: Unique identifier for the stored resource.
            filename: Name of the file.

        Returns:
            Path: Full path to the file.
        """
        return self.get_storage_path(identifier) / filename

    def get_file(self, identifier: str, filename: str) -> bytes | None:
        """
        Retrieve a file's contents by its identifier and filename.

        Args:
            identifier: Unique identifier for the stored resource.
            filename: Name of the file.

        Returns:
            bytes | None: File contents if found, otherwise None.
        """
        target = self.get_filepath(identifier, filename)
        if target.exists() and target.is_file():
            return target.read_bytes()
        return None

    def save_file(
        self,
        identifier: str,
        filename: str,
        content: Union[str, dict, list, bytes, bytearray],
        overwrite: bool = True,
    ) -> Path:
        """
        Save a file to the directory for a given identifier.

        Args:
            identifier: Unique identifier for the stored resource.
            filename: Target filename.
            content: File content (string, dict, list, or bytes).
            overwrite: Whether to overwrite the file if it already exists.

        Returns:
            Path: Path to the saved file.

        Raises:
            ValueError: If overwrite is False and the file already exists.
        """
        file_path = self.get_storage_path(identifier) / filename

        if not overwrite and file_path.exists():
            raise ValueError(f"Cannot overwrite file {file_path}")

        if isinstance(content, (dict, list)):
            file_path.write_text(json.dumps(content, indent=2))
        elif isinstance(content, (bytes, bytearray)):
            mode = "wb" if overwrite else "xb"
            with open(file_path, mode) as f:
                f.write(content)
        else:
            file_path.write_text(str(content))

        return file_path

    def list_file_paths(self, identifier: str) -> List[Path]:
        """
        List all file paths under a given identifier directory.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            List[Path]: List of file paths under the directory.
        """
        target = self.get_storage_path(identifier)
        if not target.exists():
            logger.warning(f"Target path does not exist for {identifier}")
            return []
        return [f for f in target.iterdir() if f.is_file]

    def list_file_names(self, identifier: str) -> List[str]:
        """
        List all file names under a given identifier directory.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            List[str]: List of file names.
        """
        return [f.name for f in self.list_file_paths(identifier)]

    def delete_storage(self, identifier: str) -> None:
        """
        Delete a storage directory and all its contents.

        Args:
            identifier: Unique identifier for the stored resource.
        """
        target = self.get_storage_path(identifier)
        if target.exists():
            for f in target.iterdir():
                if f.is_file():
                    f.unlink()
            shutil.rmtree(target)

    def delete_file(self, identifier: str, filename: str) -> None:
        """
        Delete a specific file within a resource directory.

        Args:
            identifier: Unique identifier for the stored resource.
            filename: Name of the file to delete.
        """
        target = self.get_filepath(identifier, filename)
        if target and target.exists():
            target.unlink()

    # -------------------------------------------------------------------------
    # Download utilities
    # -------------------------------------------------------------------------

    async def download_question(self, identifier: str) -> bytes:
        """
        Bundle all files for a given identifier into an in-memory ZIP archive.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            bytes: In-memory ZIP file containing the resource's files.
        """
        logger.debug("Attempting to download questions")
        files = self.list_file_paths(identifier)
        logger.debug(f"Preparing download for {identifier}")
        return await self.file_service.download_zip(files, folder_name=identifier)
