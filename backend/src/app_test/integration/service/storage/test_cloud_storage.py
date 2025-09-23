# --- Standard Library ---
from pathlib import Path
from typing import Dict, Tuple

# --- Third-Party ---
import pytest

# --- Internal ---
from src.api.core import settings, logger


@pytest.fixture
def save_file(cloud_storage_service) -> Tuple[Path, Dict[str, str]]:
    """
    Saves a test file to Firebase and returns its path and metadata.
    """
    file_data = {
        "identifier": "test_folder",
        "filename": "hello.txt",
        "content": "Hello Firebase!",
    }
    blob_path = cloud_storage_service.save_file(
        file_data["identifier"], file_data["filename"], file_data["content"]
    )
    return blob_path, file_data


# ----------------------
# Tests
# ----------------------
def test_save_file(save_file):
    """
    Ensure saving a file returns the expected blob path.
    """
    blob_path, file_data = save_file
    expected_path = (
        Path("integration_test") / file_data["identifier"] / file_data["filename"]
    )
    assert blob_path == expected_path


def test_get_file(cloud_storage_service, save_file):
    """
    Ensure a saved file can be retrieved with its correct content.
    """
    _, file_data = save_file
    content = cloud_storage_service.get_file(
        file_data["identifier"], filename=file_data["filename"]
    )
    assert content is not None
    assert content.decode("utf-8") == file_data["content"]


def test_does_directory_exist(cloud_storage_service, save_file):
    _, file_data = save_file
    exist = cloud_storage_service.does_directory_exist(file_data["identifier"])
    assert exist


def test_delete_file(cloud_storage_service, save_file):
    """
    Ensure a saved file can be deleted and is no longer retrievable.
    """
    _, file_data = save_file

    # Confirm file exists
    assert cloud_storage_service.does_file_exist(
        file_data["identifier"], file_data["filename"]
    )

    # Delete file
    cloud_storage_service.delete_file(
        file_data["identifier"], filename=file_data["filename"]
    )

    # Confirm file is gone
    assert not cloud_storage_service.does_file_exist(
        file_data["identifier"], file_data["filename"]
    )
    assert (
        cloud_storage_service.get_file(
            file_data["identifier"], filename=file_data["filename"]
        )
        is None
    )


def test_get_files_names(save_file, cloud_storage_service):
    """
    Ensure file names can be listed under the given identifier.
    """
    _, file_data = save_file
    results = cloud_storage_service.get_files_names(file_data["identifier"])
    logger.debug("Retrieved filenames: %s", results)
    assert file_data["filename"] in results


def test_does_file_exist(cloud_storage_service, save_file):
    """
    Ensure does_file_exist correctly identifies existing files.
    """
    _, file_data = save_file
    exists = cloud_storage_service.does_file_exist(
        file_data["identifier"], file_data["filename"]
    )
    assert exists is True


def test_get_nonexistent_file(cloud_storage_service):
    """
    Ensure retrieving a non-existent file returns None.
    """
    content = cloud_storage_service.get_file("no_folder", "missing.txt")
    assert content is None
