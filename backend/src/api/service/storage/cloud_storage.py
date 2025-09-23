# --- Standard Library ---
import json
from pathlib import Path
from typing import List, Tuple

# --- Third-Party ---
import firebase_admin
from firebase_admin import credentials, storage
from google.cloud.exceptions import NotFound
from google.cloud.storage.blob import Blob

# --- Internal ---
from .base import StorageService
from src.api.core import settings, logger
from src.utils import safe_dir_name


# Define the credentials
if not settings.FIREBASE_PATH:
    raise ValueError("Firebase Credentials Not Found")


class FireCloudStorageService(StorageService):
    """
    Cloud storage service implementation using Firebase Admin SDK.

    This service provides CRUD-like operations for files stored in a Firebase
    (Google Cloud Storage) bucket. Files are organized under a base directory
    (e.g., "questions") and grouped by identifier subdirectories.
    """

    def __init__(
        self, cred_path: str | Path, bucket_name: str, base_name: str = "questions"
    ):
        """
        Initialize the Firebase Cloud Storage service.

        Parameters
        ----------
        cred_path : str | Path
            Path to the Firebase service account key JSON file.
        bucket_name : str
            Name of the Firebase (Google Cloud Storage) bucket.
        base_name : str, optional
            Base directory (prefix) for organizing files in the bucket.
        """
        # Initialize Firebase only once
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"storageBucket": bucket_name})

        self.bucket = storage.bucket(bucket_name)
        self.base_dir = base_name

    def get_directory(self, identifier: str) -> Path:
        """
        Get the directory path for a given identifier.

        Parameters
        ----------
        identifier : str
            The unique identifier for the group of files.

        Returns
        -------
        Path
            Path object representing the directory for this identifier.
        """
        return Path(self.base_dir) / safe_dir_name(identifier)

    def create_directory(self, identifier: str) -> Path | Blob:
        blob = self.bucket.blob(self.get_directory(identifier).as_posix())
        blob.upload_from_string("")
        return blob

    def get_filepath(self, identifier: str, filename: str) -> Path:
        """
        Build the full file path for an identifier and filename.

        Parameters
        ----------
        identifier : str
            The group identifier (like a folder name).
        filename : str
            The name of the file.

        Returns
        -------
        Path
            Path object representing the full path to the file.
        """
        return self.get_directory(identifier) / filename

    def get_blob(self, identifier: str, filename: str) -> Blob:
        """
        Get the Blob object for a given identifier and filename.

        Parameters
        ----------
        identifier : str
            The group identifier (like a folder name).
        filename : str
            The name of the file.

        Returns
        -------
        Blob
            Google Cloud Storage Blob object.
        """
        file_path = self.get_filepath(identifier, filename)
        blob = self.bucket.blob(str(file_path.as_posix()))
        return blob

    def save_file(
        self,
        identifier: str,
        filename: str,
        content: str | dict | List | bytes | bytearray,
        overwrite: bool = True,
    ) -> Path:
        """
        Save a file to Firebase storage.

        Parameters
        ----------
        identifier : str
            The group identifier (like a folder name).
        filename : str
            The name of the file to save.
        content : str | dict | list | bytes | bytearray
            The file content to save. Dicts/lists are serialized as JSON.
        overwrite : bool, optional
            Whether to overwrite the file if it already exists.

        Returns
        -------
        Path
            The expected path (prefix + identifier + filename) for the file.
        """
        blob = self.get_blob(identifier, filename)

        if isinstance(content, (dict, list)):
            content = json.dumps(content, indent=2)
        elif isinstance(content, (bytes, bytearray)):
            content = content.decode()
        elif isinstance(content, str):
            pass
        else:
            raise ValueError(f"Could not write content of type {type(content)}")

        blob.upload_from_string(data=content)
        return self.get_filepath(identifier, filename)

    def get_file(self, identifier: str, filename: str) -> bytes | None:
        """
        Retrieve a file from Firebase storage.

        Parameters
        ----------
        identifier : str
            The group identifier (like a folder name).
        filename : str
            The name of the file to retrieve.

        Returns
        -------
        bytes | None
            File content as bytes if the file exists, else None.
        """
        if self.does_file_exist(identifier, filename):
            blob = self.get_blob(identifier, filename)
            return blob.download_as_bytes()
        return None

    def does_file_exist(self, identifier: str, filename: str) -> bool:
        """
        Check if a file exists in Firebase storage.

        Parameters
        ----------
        identifier : str
            The group identifier (like a folder name).
        filename : str
            The name of the file.

        Returns
        -------
        bool
            True if the file exists, False otherwise.
        """
        blob = self.get_blob(identifier, filename)
        return blob.exists()

    def does_directory_exist(self, identifier: str) -> bool:
        prefix = f"{self.get_directory(identifier).as_posix().rstrip('/')}/"
        logger.debug("Checking if blob exist %s", prefix)
        blobs = list(self.bucket.list_blobs(prefix=prefix, max_results=1))
        logger.debug("These are all the blobs %s", blobs)

        blob = self.bucket.blob(self.get_directory(identifier).as_posix())
        if blob.exists():
            logger.debug("Found blob it exist")
            return True
        elif len(blobs) > 0 and not blob.exists():
            return False
        return False

    def delete_file(self, identifier: str, filename: str) -> None:
        """
        Delete a file from Firebase storage if it exists.

        Parameters
        ----------
        identifier : str
            The group identifier (like a folder name).
        filename : str
            The name of the file.

        Returns
        -------
        None
        """
        if self.does_file_exist(identifier, filename):
            blob = self.get_blob(identifier, filename)
            blob.delete()
        return None

    def hard_delete(self) -> None:
        blobs = self.bucket.list_blobs(prefix=str(self.base_dir))
        try:
            for blob in blobs:
                logger.info(f"Deleting {blob.name}")
                blob.delete()
        except NotFound:
            print("Blob not found, nothing to delete.")
        return

    def get_files_names(self, identifier: str) -> List[str]:
        """
        List all file names under the given identifier.

        Parameters
        ----------
        identifier : str
            The group identifier (like a folder name).

        Returns
        -------
        List[str]
            List of file names under the given identifier.
        """
        filepath = self.get_directory(identifier)
        prefix = filepath.as_posix()
        files = []
        for blob in self.bucket.list_blobs(prefix=prefix):
            logger.debug("This is the blob %s", blob.name)
            relative_path = blob.name[len(prefix) :]
            logger.debug("This is the relative path %s", relative_path)
            if relative_path:
                files.append(relative_path.split("/")[-1])
        return files

    def delete_all(self, identifier: str) -> None:
        filepath = self.get_directory(identifier)
        prefix = filepath.as_posix()
        for blob in self.bucket.list_blobs(prefix=prefix):
            try:
                logger.info(f"Deleting {blob.name}")
                blob.delete()
            except NotFound:
                logger.error("Blob not found, nothing to delete.")
            return
