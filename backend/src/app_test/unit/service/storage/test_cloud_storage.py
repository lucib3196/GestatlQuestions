from unittest.mock import MagicMock
from src.api.service.storage.cloud_storage import FireCloudStorageService
from src.api.core import logger
import pytest
from typing import Type, Tuple, Dict
from pathlib import Path
import io
import zipfile
import json


@pytest.fixture
def fake_cloud_storage(
    monkeypatch,
) -> Tuple[FireCloudStorageService, Dict[str, str], MagicMock, MagicMock]:
    fake_cred = MagicMock()
    fake_bucket = MagicMock()
    fake_blob = MagicMock()
    fake_bucket.blob.return_value = fake_blob
    monkeypatch.setattr(
        "src.api.service.storage.cloud_storage.credentials.Certificate",
        lambda _: fake_cred,
    )
    monkeypatch.setattr(
        "src.api.service.storage.cloud_storage.firebase_admin.initialize_app",
        lambda cred, opts: MagicMock(),
    )
    monkeypatch.setattr(
        "src.api.service.storage.cloud_storage.storage.bucket",
        lambda *args, **kwargs: fake_bucket,
    )
    
    

    data = {
        "cred_path": "fake.json",
        "bucket_name": "test-bucket",
        "base_name": "questions",
    }
    service = FireCloudStorageService(
        cred_path=data["cred_path"],
        bucket_name=data["bucket_name"],
        base_name=data["base_name"],
    )
    return service, data, fake_bucket, fake_blob


@pytest.fixture
def dummy_data():
    return {
        "identifier": "TestFolder",
        "filename": "text.txt",
        "content": "Hello World",
    }


@pytest.fixture
def save_dummy_data(dummy_data, fake_cloud_storage):
    service, data, fake_bucket, fake_blob = fake_cloud_storage

    return service.save_file(
        dummy_data["identifier"], dummy_data["filename"], dummy_data["content"]
    )


def test_cloud_init(fake_cloud_storage):
    service, data, fake_bucket, fake_blob = fake_cloud_storage
    assert service.bucket == fake_bucket


def test_save_file(fake_cloud_storage, dummy_data, save_dummy_data):
    service, data, fake_bucket, fake_blob = fake_cloud_storage
    identifier = dummy_data["identifier"]
    filename = dummy_data["filename"]
    content = dummy_data["content"]

    expected_path = (Path(data["base_name"]) / identifier / filename).as_posix()

    # Assert values
    fake_bucket.blob.assert_called_once_with(expected_path)
    fake_blob.upload_from_string.assert_called_once_with(data=content)

    assert save_dummy_data.as_posix() == expected_path


def test_get_file(fake_cloud_storage, dummy_data, save_dummy_data):
    service, data, fake_bucket, fake_blob = fake_cloud_storage

    fake_blob.exists.return_value = True
    fake_blob.download_as_bytes.return_value = b"Hello World"
    content = service.get_file(dummy_data["identifier"], dummy_data["filename"])
    assert content == b"Hello World"


#TODO: Clean up this file have a better unit test and make this test more robuts

# @pytest.mark.asyncio
# async def test_download_question(save_dummy_data, fake_cloud_storage, dummy_data):
#     service = fake_cloud_storage[0]
#     data = await service.download_question("TestFolder")
    
#     fake_bucket.list_blobs.return_value = [fake_blob]

#     assert isinstance(data, bytes)
#     assert len(data) > 0
#     buffer = io.BytesIO(data)
#     with zipfile.ZipFile(buffer, "r") as z:
#         names = z.namelist()

#         assert f"TestFolder/{dummy_data["filename"]}" in names
