from fastapi import Depends
from src.api.core import logger
from src.api.core.config import get_settings
from src.storage import FirebaseStorage, LocalStorageService, StorageService
from typing import Annotated

settings = get_settings()
def get_storage_manager() -> StorageService:
    if settings.STORAGE_SERVICE == "cloud":
        if not (settings.FIREBASE_CRED and settings.STORAGE_BUCKET):
            raise ValueError("Settings for Cloud Storage not Set")
        storage_service = FirebaseStorage(
            base_path="/UCR_Questions", bucket=settings.STORAGE_BUCKET
        )
    else:
        storage_service = LocalStorageService(settings.QUESTIONS_PATH)
    logger.info(f"Question manager set to {settings.STORAGE_SERVICE}")
    logger.info("Initialized Question Manager Success ")
    return storage_service


QuestionManagerDependency = Annotated[StorageService, Depends(get_storage_manager)]
