from pathlib import Path
from typing import Union, Optional, List
from google.cloud.storage.blob import Blob
from typing import IO, Optional


from pathlib import Path
from typing import IO, List, Optional
from google.cloud.storage.blob import Blob


class StorageService:
    """
    Base storage interface for managing files and directories.

    This abstract class defines the core methods required for any storage backend.
    Subclasses should implement these methods based on the underlying storage mechanism
    (e.g., local filesystem, cloud bucket, or hybrid configuration).
    """

    # -------------------------------------------------------------------------
    # Base path and metadata
    # -------------------------------------------------------------------------
    def get_base_path(self) -> str | Path:
        """Return the absolute path (or URI) to the base storage directory or bucket."""
        raise NotImplementedError("get_base_path must be implemented by subclass")

    # -------------------------------------------------------------------------
    # Storage path operations
    # -------------------------------------------------------------------------
    def get_storage_path(self, target: str | Path) -> str | Path:
        """Return the absolute path to the directory for a given storage target."""
        raise NotImplementedError("get_storage_path must be implemented by subclass")

    def create_storage_path(self, target: str | Path) -> Path | Blob:
        """Create a new directory or container for the given storage target."""
        raise NotImplementedError("create_storage_path must be implemented by subclass")

    def get_relative_storage_path(self, target: str | Path) -> str | Path:
        """Return the relative path (from the base directory) for the given storage target."""
        raise NotImplementedError(
            "get_relative_storage_path must be implemented by subclass"
        )

    def does_storage_path_exist(self, target: str | Path) -> bool:
        """Check whether a storage directory or container exists for the given target."""
        raise NotImplementedError(
            "does_storage_path_exist must be implemented by subclass"
        )

    # -------------------------------------------------------------------------
    # File operations
    # -------------------------------------------------------------------------
    def get_file(
        self, target: str | Path, filename: Optional[str] = None
    ) -> Optional[bytes]:
        """Retrieve the raw contents of a file for a given target."""
        raise NotImplementedError("get_file must be implemented by subclass")

    def get_filepath(
        self, target: str | Path, filename: Optional[str] = None
    ) -> str | Path:
        """Return the absolute path to a specific file inside a given target directory."""
        raise NotImplementedError("get_filepath must be implemented by subclass")

    def upload_file(
        self,
        file_obj: IO[bytes],
        target: str | Path,
        filename: Optional[str] = None,
        content_type: str = "application/octet-stream",
    ) -> Blob | Path:
        """Upload a file object to a specific path in the storage backend."""
        raise NotImplementedError("upload_file must be implemented by subclass")

    def save_file(
        self,
        target: str | Path,
        filename: str,
        content: str | dict | list | bytes | bytearray,
        overwrite: bool = True,
    ) -> Path | str:
        """Save a file under the given target directory."""
        raise NotImplementedError("save_file must be implemented by subclass")

    def list_files(self, target: str | Path) -> List[str]:
        """List all file names under a given target directory."""
        raise NotImplementedError("list_files must be implemented by subclass")

    def delete_storage(self, target: str | Path) -> None:
        """Delete an entire storage directory or container for the given target."""
        raise NotImplementedError("delete_storage must be implemented by subclass")

    def delete_file(self, target: str | Path, filename: str) -> None:
        """Delete a specific file under a given target directory."""
        raise NotImplementedError("delete_file must be implemented by subclass")

    def hard_delete(self) -> None:
        """Completely remove all storage contents (destructive operation)."""
        raise NotImplementedError("hard_delete must be implemented by subclass")
