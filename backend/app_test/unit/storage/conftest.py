from src.storage import LocalStorageService
import pytest

# --- Internal ---
from src.api.core import logger
from src.api.core.config import get_settings
from src.storage import LocalStorageService
from src.storage.local_storage import LocalStorageService
from src.firebase.firebase_storage import FirebaseStorage
from src.firebase.core import initialize_firebase_app

settings = get_settings()
initialize_firebase_app()


# Storage Fixtures
@pytest.fixture(scope="function")
def cloud_storage_service():
    """
    Provides a FireCloudStorageService connected to the configured test bucket.
    """

    base_path = "integration_test"
    settings.STORAGE_BUCKET

    return FirebaseStorage(settings.STORAGE_BUCKET, base_path)


@pytest.fixture(autouse=True)
def clean_up_cloud(cloud_storage_service):
    # Setup code (before test runs)
    yield
    # Teardown code (after test finishes)
    cloud_storage_service.hard_delete()
    logger.debug("Deleting Bucket Cleaning Up")


@pytest.fixture
def local_storage(tmp_path):
    """Provide a LocalStorageService rooted in a temp directory."""
    base = tmp_path / "questions"
    return LocalStorageService(base)


@pytest.fixture(
    scope="function",
)
def question_manager(request, question_manager_local, question_manager_cloud):
    storage_type = request.param
    if storage_type == "cloud":
        qm = question_manager_cloud
    elif storage_type == "local":
        qm = question_manager_local
    else:
        raise ValueError("Incorrect storage type")
    return qm
