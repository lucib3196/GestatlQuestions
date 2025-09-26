# --- Standard Library ---
import json
from pathlib import Path
from typing import Tuple

# --- Third-Party ---
import pytest
import io

# --- Internal ---
from src.api.service.storage import local_storage as ls
from src.api.core import logger
import zipfile


@pytest.fixture
def create_test_dir(local_storage) -> Tuple[Path, str]:
    testdir = "TestFolder"
    created_dir = local_storage.create_directory(testdir)
    return created_dir, testdir


@pytest.fixture
def save_multiple_files(local_storage, create_test_dir):
    _, name = create_test_dir
    files = [
        ("text.txt", "Hello World"),  # string
        ("data.json", {"key": "value"}),  # dict
        ("binary.bin", b"\x00\x01\x02"),  # bytes
    ]

    for filename, content in files:
        local_storage.save_file(name, filename, content)

    return files


def test_local_storage_init(local_storage):
    assert local_storage


def test_create_directory(create_test_dir):
    created, name = create_test_dir
    assert created.exists()
    assert created.name == name


@pytest.mark.parametrize(
    "filename, content, reader",
    [
        ("text.txt", "Hello World", lambda f: f.read_text()),  # string
        ("data.json", {"key": "value"}, lambda f: json.loads(f.read_text())),  # dict
        ("binary.bin", b"\x00\x01\x02", lambda f: f.read_bytes()),  # bytes
    ],
)
def test_save_file(local_storage, create_test_dir, filename, content, reader):
    _, name = create_test_dir
    f = local_storage.save_file(name, filename, content)
    assert f.exists()
    assert reader(f) == content


def test_empty_directory(create_test_dir, local_storage):
    _, name = create_test_dir
    f = local_storage.get_files_names(name)
    assert f == []


def test_list_file_names(create_test_dir, local_storage, save_multiple_files):
    _, name = create_test_dir
    f = local_storage.get_files_names(name)
    assert len(f) == len(save_multiple_files)

    for fname, _ in save_multiple_files:
        assert fname in f


def test_delete_file(create_test_dir, local_storage, save_multiple_files):
    _, name = create_test_dir
    for filename, _ in save_multiple_files:
        local_storage.delete_file(name, filename)
        assert local_storage.get_file(name, filename) is None


def test_get_file(create_test_dir, local_storage, save_multiple_files):
    _, name = create_test_dir

    for filename, expected in save_multiple_files:
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


@pytest.mark.asyncio
async def test_download_zip(tmp_path, local_storage, save_multiple_files):
    data = await local_storage.download_question("TestFolder")

    assert isinstance(data, bytes)
    assert len(data) > 0
    buffer = io.BytesIO(data)
    with zipfile.ZipFile(buffer, "r") as z:
        names = z.namelist()
        for f in save_multiple_files:
            assert f"TestFolder/{f[0]}" in names
