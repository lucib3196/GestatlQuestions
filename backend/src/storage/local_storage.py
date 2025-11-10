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

    def __init__(self, root: str | Path, base: str, create: bool = False):
        """
        Initialize the local storage service with a base directory.

        Args:
            root: Path or string specifying the root storage directory.
        """
        # Where the storage is at
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

        # Base name the folder where we store
        self.base_name = base
        self.base_path = self.root / base
        logger.debug(
            "Initialized the storage, questions will be stored at %s", self.root
        )

    # Helper
    def normalize_path(self, target: str | Path) -> str:
        """
        Ensure the given path is normalized under the base path.

        - If an absolute path is passed, it strips self.root and returns a relative path.
        - If a relative path is passed, it ensures it is prefixed by self.base_name.
        - Always returns a POSIX-style string (forward slashes).
        """
        # Convert to Path
        target_path = Path(target)

        # Case 1: Absolute path inside the storage root
        try:
            relative_path = target_path.relative_to(self.root)
        except ValueError:
            # Case 2: Not inside root (likely already relative or external)
            relative_path = target_path

        # Convert to posix string
        rel_str = relative_path.as_posix()

        # Case 3: Ensure prefix
        if not rel_str.startswith(f"{self.base_name}/"):
            rel_str = f"{self.base_name}/{rel_str}"

        return rel_str

    # -------------------------------------------------------------------------
    # Base path operations
    # -------------------------------------------------------------------------

    def get_base_path(self) -> str:
        """
        Return the absolute path to the base directory for local storage.

        Returns:
            Path: The resolved base directory path.
        """
        return Path(self.base_path).as_posix()

    def get_root_path(self) -> str:
        """Returns the root path"""
        return self.root.as_posix()

    # Getting

    def get_storage_path(self, target: str | Path | Blob, relative: bool = True) -> str:
        """
        Build the absolute path for a resource based on its identifier.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            Path: Path to the resource directory.
        """
        if isinstance(target, Blob):
            target = str(target.name)
        target = self.normalize_path(target)

        absolute_path = Path(self.root) / str(target)
        if relative:
            return absolute_path.relative_to(self.root).as_posix()

        return absolute_path.as_posix()

    def create_storage_path(self, target: str | Path) -> Path:
        """
        Create a directory for the given identifier if it does not exist.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            Path: Path to the created directory.
        """
        storage = Path(self.get_storage_path(target, relative=False))
        storage.mkdir(parents=True, exist_ok=True)
        return storage

    def does_storage_path_exist(self, target: str | Path) -> bool:
        """
        Check if a directory exists for a given identifier.

        Args:
            identifier: Unique identifier for the stored resource.

        Returns:
            bool: True if the directory exists, False otherwise.
        """
        return Path(self.get_storage_path(target, relative=False)).exists()

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
            path = Path(self.get_storage_path(target, relative=False)) / filename
            return path.as_posix()
        else:
            return self.get_storage_path(target)

    def get_filepath(
        self, target: str | Path, filename: str | None = None, recursive: bool = False
    ):
        if filename:
            path = Path(self.get_storage_path(target, relative=False)) / filename
            return path.as_posix()
        else:
            return self.get_storage_path(target, relative=False)

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
        file_path = Path(self.get_storage_path(target, relative=False)) / filename

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
        target = Path(self.get_storage_path(target, relative=False))
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
        target = Path(self.get_base_path())
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
        target = Path(self.get_filepath(target, filename))
        logger.debug(f"[LOCAL STORAGE] Attempting to delete [target]: {target}")
        if target and target.exists():
            logger.debug(f"[LOCAL STORAGE] Deleting file {target}")
            target.unlink()
        else:
            logger.warning("File does not exist")

    def rename_storage(self, old: str | Path, new: str | Path) -> str:
        old = Path(old)
        new = Path(new)

        if not old.is_absolute():
            old = self.get_storage_path(old, relative=False)
        if not new.is_absolute():
            new = self.get_storage_path(new, relative=False)

        Path(old).rename(new)
        return Path(new).as_posix()
