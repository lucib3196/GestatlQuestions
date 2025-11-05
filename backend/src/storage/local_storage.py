# --- Standard Library ---
import json
from pathlib import Path
from typing import List, Union
import shutil

# --- Internal ---
from .base import StorageService
from src.api.core import logger
from src.utils import safe_dir_name
from google.cloud.storage.blob import Blob


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
        self.root = Path(root).resolve().parent  # => C:\Github\GestatlQuestions
        self.root.mkdir(parents=True, exist_ok=True)

        logger.debug(
            "Initialized the storage, questions will be stored at %s", self.root
        )

    # -------------------------------------------------------------------------
    # Base path operations
    # -------------------------------------------------------------------------

    def get_base_path(self) -> str:
        """
        Return the absolute path to the base directory for local storage.

        Returns:
            Path: The resolved base directory path.
        """
        return (self.root).as_posix()

    def get_storage_path(self, target: str | Path | Blob) -> str:
        """
        Build the absolute path for a resource based on its identifier.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            Path: Path to the resource directory.
        """
        return (Path(self.root) / str(target)).as_posix()

    def create_storage_path(self, target: str | Path) -> Path:
        """
        Create a directory for the given identifier if it does not exist.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            Path: Path to the created directory.
        """
        storage = Path(self.get_storage_path(target))
        storage.mkdir(parents=True, exist_ok=True)
        return storage

    def get_relative_storage_path(self, target: str | Path | Blob):
        """
        Return the relative path of a storage directory from the base root.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            Path: Relative path to the storage directory.
        """
        # Assuming you are running it from backend folder
        return Path(self.root) / str(target)

    def does_storage_path_exist(self, target: str | Path) -> bool:
        """
        Check if a directory exists for a given identifier.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        return Path(self.get_storage_path(target)).exists()

    # -------------------------------------------------------------------------
    # File access and management
    # -------------------------------------------------------------------------

    def get_file(
        self, target: str | Path, filename: str | None = None, recursive: bool = False
    ) -> str:
        """
        Build the absolute file path for a given identifier and filename.

        Args:
            identifier: Unique identifier for the stored resource.
            filename: Name of the file.

        Returns:
            Path: Full path to the file.
        """
        if filename:
            path = Path(self.get_storage_path(target)) / filename
            return path.as_posix()
        else:
            return self.get_storage_path(target)

    def read_file(
        self, target: str | Path, filename: str | None = None
    ) -> bytes | None:
        """
        Retrieve a file's contents by its identifier and filename.

        Args:
            identifier: Unique identifier for the stored resource.
            filename: Name of the file.

        Returns:
            bytes | None: File contents if found, otherwise None.
        """
        target = Path(self.get_file(target, filename))

        if target.exists() and target.is_file():
            return target.read_bytes()
        return None

    def save_file(
        self,
        target: str | Path,
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
        file_path = Path(self.get_storage_path(target)) / filename

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

    def list_filepaths(self, target: str | Path, recursive: bool = False) -> List[Path]:
        """
        List all file paths under a given identifier directory.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            List[Path]: List of file paths under the directory.
        """
        target = Path(self.get_storage_path(target))
        if not target.exists():
            logger.warning(f"Target path does not exist for {target}")
            return []
        if recursive:
            return [f for f in target.rglob("*")]
        else:
            return [f for f in target.iterdir()]

    def list_files(self, target: str | Path) -> List[str]:
        """
        List all file names under a given identifier directory.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            List[str]: List of file names.
        """
        return [f.name for f in self.list_filepaths(target) if f.is_file()]

    def delete_storage(self, target: str | Path) -> None:
        """
        Delete a storage directory and all its contents.

        Args:
            identifier: Unique identifier for the stored resource.
        """
        target = Path(self.get_storage_path(target))
        logger.info(f"Target to delete {target}")
        if target.exists():
            for f in target.iterdir():
                if f.is_file():
                    f.unlink()
            shutil.rmtree(target)

    def hard_delete(self) -> None:
        target = self.root
        if target.exists():
            for f in target.iterdir():
                if f.is_file():
                    f.unlink()
            shutil.rmtree(target)

    def delete_file(self, target: str | Path, filename: str | None = None) -> None:
        """
        Delete a specific file within a resource directory.

        Args:
            identifier: Unique identifier for the stored resource.
            filename: Name of the file to delete.
        """
        target = Path(self.get_file(target, filename))
        logger.debug(f"[LOCAL STORAGE] Attempting to delete [target]: {target}")
        if target and target.exists():
            logger.debug(f"[LOCAL STORAGE] Deleting file {target}")
            target.unlink()

    def rename_storage(self, old: str | Path, new: str | Path) -> str:
        old = self.get_storage_path(old)
        new = self.get_storage_path(new)
        return Path(old).rename(new).as_posix()
