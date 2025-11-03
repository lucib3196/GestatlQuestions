import io
import json
import zipfile
from pathlib import Path
from typing import Tuple
import pytest


@pytest.fixture
def create_test_dir(local_storage) -> Tuple[Path, str]:
    """Create a temporary test directory inside the local storage."""
    testdir = "TestFolder"
    created_dir = local_storage.create_storage_path(testdir).as_posix()
    return created_dir, testdir


@pytest.fixture
def save_multiple_files(local_storage, create_test_dir):
    """Save multiple test files (string, dict, bytes) under a temporary directory."""
    _, name = create_test_dir
    files = [
        ("text.txt", "Hello World"),  # string
        ("data.json", {"key": "value"}),  # dict
        ("binary.bin", b"\x00\x01\x02"),  # bytes
    ]

    for filename, content in files:
        local_storage.save_file(name, filename, content)

    return files, name


# =============================================================================
# Initialization Tests
# =============================================================================
def test_initialization(local_storage, tmp_path):
    """Ensure storage initializes with correct root and base properties."""
    assert local_storage.root == (tmp_path / "questions")
    assert local_storage.get_base_path() == (tmp_path / "questions").as_posix()


# =============================================================================
# Directory Management Tests
# =============================================================================
def test_create_storage_path(create_test_dir):
    """Ensure storage directory is created successfully."""
    created, folder_name = create_test_dir
    created_path = Path(created)
    assert created_path.exists()
    assert created_path.name == folder_name


def test_get_storage_path(create_test_dir, local_storage):
    """Validate that get_storage_path returns the correct directory path."""
    created, folder_name = create_test_dir
    assert local_storage.get_storage_path(folder_name) == created


def test_get_relative_storage_path(create_test_dir, local_storage):
    """Check that relative path is computed correctly from base root."""
    _, folder_name = create_test_dir
    assert (
        Path(local_storage.get_relative_storage_path(folder_name))
        == Path("questions") / folder_name
    )


def test_does_storage_path_exist(create_test_dir, local_storage):
    """Verify directory existence check returns True for valid paths."""
    _, folder_name = create_test_dir
    assert local_storage.does_storage_path_exist(folder_name)


# =============================================================================
# File Utilities Tests
# =============================================================================
@pytest.mark.parametrize(
    "filename, content, reader",
    [
        ("text.txt", "Hello World", lambda f: f.read_text()),  # string
        ("data.json", {"key": "value"}, lambda f: json.loads(f.read_text())),  # dict
        ("binary.bin", b"\x00\x01\x02", lambda f: f.read_bytes()),  # bytes
    ],
)
def test_save_file(local_storage, create_test_dir, filename, content, reader):
    """Ensure save_file correctly writes different content types."""
    _, name = create_test_dir
    f = local_storage.save_file(name, filename, content)
    assert f.exists()
    assert reader(f) == content


def test_get_filepath(save_multiple_files, local_storage, tmp_path):
    """Validate get_filepath returns expected absolute paths."""
    files, folder_name = save_multiple_files
    for f in files:
        assert (
            local_storage.get_filepath(folder_name, f[0])
            == (Path(tmp_path) / "questions" / folder_name / f[0]).as_posix()
        )


def test_empty_directory(create_test_dir, local_storage):
    """Check that a newly created directory is empty."""
    _, name = create_test_dir
    f = local_storage.list_files(name)
    assert f == []


def test_list_file_names(save_multiple_files, local_storage):
    """Ensure list_file_names returns all stored filenames."""
    files, name = save_multiple_files
    retrieved_files = local_storage.list_files(name)

    assert len(retrieved_files) == len(files)
    for fname, _ in files:
        assert fname in retrieved_files


def test_delete_file(save_multiple_files, local_storage):
    """Ensure delete_file removes files as expected."""
    files, name = save_multiple_files
    for filename, _ in files:
        local_storage.delete_file(name, filename)
        assert local_storage.get_file(name, filename) is None


def test_get_file(save_multiple_files, local_storage):
    """Verify get_file correctly retrieves stored file contents."""
    files, name = save_multiple_files

    for filename, expected in files:
        content = local_storage.get_file(name, filename)
        assert content is not None, f"File {filename} should exist"

        if isinstance(expected, str):
            assert content.decode("utf-8") == expected

        elif isinstance(expected, (dict, list)):
            loaded = json.loads(content.decode("utf-8"))
            assert loaded == expected

        elif isinstance(expected, (bytes, bytearray)):
            assert content == expected

        else:
            raise TypeError(f"Unsupported type: {type(expected)}")

