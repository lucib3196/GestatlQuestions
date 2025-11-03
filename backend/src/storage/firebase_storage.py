# --- Standard Library ---
from pathlib import Path
from typing import IO, List, Optional, Union
import json

# --- Third-Party ---
from firebase_admin import storage
from google.cloud.exceptions import NotFound
from google.cloud.storage.blob import Blob

# --- Local Modules ---
from src.api.core.logging import logger
from src.storage.base import StorageService
from src.api.service.file_service import get_content_type


class FirebaseStorage(StorageService):
    def __init__(self, bucket, base_path):
        logger.info("[Firebase]: Intializing firebase storage ")
        self.bucket = storage.bucket(bucket)
        self.base_path = base_path

    def get_base_path(self) -> str | Path:
        return Path(self.base_path).as_posix()

    def get_storage_path(self, target: str | Path | Blob) -> str:
        return (Path(self.base_path) / str(target)).as_posix()

    def get_relative_storage_path(self, target: str | Path | Blob) -> str | Path:
        return Path(self.get_storage_path(target)).relative_to(
            Path(self.base_path).parent
        )

    def create_storage_path(self, target: str | Path) -> str:
        target_blob = self.get_storage_path(target)
        blob: Blob = self.bucket.blob(target_blob)
        blob.upload_from_string("")
        return str(blob.name)

    def does_storage_path_exist(self, target: str | Path) -> bool:
        target = self.get_storage_path(target)
        blobs = list(self.bucket.list_blobs(prefix=target, max_results=1))
        blob = self.bucket.blob(target)
        if blob.exists():
            return True
        return len(blobs) > 0

    def get_filepath(self, target: str | Path, filename: str | None = None) -> str:
        target = self.get_storage_path(target)
        if filename:
            target = (Path(target) / filename).as_posix()
        return target

    def upload_file(
        self,
        file_obj: IO[bytes],
        target: str | Path,
        filename: str | None = None,
        content_type: str = "application/octet-stream",
    ) -> Blob:
        destination_blob = self.get_filepath(target, filename)
        blob = self.bucket.blob(destination_blob)
        if isinstance(file_obj, bytes):
            blob.upload_from_string(file_obj, content_type=content_type)
        else:
            try:
                file_obj.seek(0)
            except Exception:
                pass  # not all IO objects support seek
        blob.upload_from_file(file_obj, content_type=content_type)
        return blob

    def save_file(
        self,
        target: str | Path,
        filename: str,
        content: Union[str, dict, list, bytes, bytearray],
        overwrite: bool = True,
    ) -> str:
        """
        Save a file to Firebase storage.

        Dicts/lists are serialized as JSON. Bytes/bytearray are decoded.
        """
        blob = self.get_blob(target, filename)

        if isinstance(content, (dict, list)):
            content = json.dumps(content, indent=2)
        elif isinstance(content, (bytes, bytearray)):
            content = content.decode()
        elif not isinstance(content, str):
            raise ValueError(f"Unsupported content type: {type(content)}")

        content_type = get_content_type(filename)
        blob.upload_from_string(data=content, content_type=content_type)

        return self.get_filepath(target, filename)

    def does_file_exist(self, target_path: str | Path, filename: str | None):
        return self.get_blob(target_path, filename).exists()

    def get_file(
        self, target: str | Path, filename: Optional[str] = None
    ) -> bytes | None:
        if self.does_file_exist(target, filename):
            return self.get_blob(target, filename).download_as_bytes()
        return None

    def get_blob(self, blob_name: str | Path, filename: Optional[str] = None) -> Blob:
        if isinstance(blob_name, Path):
            blob_name = blob_name.as_posix()
        if not filename:
            return self.bucket.blob(blob_name)
        return self.bucket.blob(self.get_filepath(blob_name, filename))

    def list_files(self, target: str | Path) -> List[str]:
        target = Path(self.get_storage_path(target)).as_posix()
        blobs = self.bucket.list_blobs(prefix=target)
        return [b.name for b in blobs]

    def delete_storage(self, target: str | Path) -> None:
        target = Path(self.get_storage_path(target)).as_posix()
        for blob in self.bucket.list_blobs(prefix=target):
            try:
                logger.info("Deleting %s", blob.name)
                blob.delete()
            except NotFound:
                logger.error("Blob not found, nothing to delete.")
        return None

    def delete_file(self, target: str | Path, filename: str) -> None:
        b = self.get_blob(target, filename)
        if b.exists():
            b.delete()

    def hard_delete(self):
        blobs = self.bucket.list_blobs(prefix=str(self.base_path))
        try:
            for blob in blobs:
                logger.info("Deleting %s", blob.name)
                blob.delete()
        except NotFound:
            logger.warning("Base directory not found, nothing to delete.")

    def rename_storage(self, old: str | Path, new: str | Path) -> str:
        """
        Rename a file (blob) in Firebase Storage by copying it to a new path
        and deleting the old one.

        Args:
            old (str | Path): The current path of the blob in Firebase Storage.
            new (str | Path): The desired new path of the blob.

        Returns:
            str: The new path after renaming.
        """
        old_path = str(old)
        new_path = str(new)

        old_blob = self.get_blob(old)

        if not old_blob.exists():
            logger.warning(f"Blob not found: {old_path}")
            return str(new_path)

        # Copy the blob to the new location
        new_blob = self.bucket.copy_blob(old_blob, self.bucket, new_path)

        # Delete the original blob
        old_blob.delete()

        print(f"[FirebaseStorage] Renamed {old_path} → {new_path}")
        return str(new_blob.name)
