from typing import Annotated, Literal

from fastapi import Depends

from src.api.core.config import get_settings, AppSettings

StorageType = Literal["local", "cloud"]


def get_app_settings() -> AppSettings:
    """
    Dependency that provides application settings from environment or config file.
    """
    return get_settings()


SettingDependency = Annotated[AppSettings, Depends(get_app_settings)]


def get_storage_type(
    settings: SettingDependency,
) -> StorageType:
    """
    Dependency that extracts the storage type from the global app settings.
    """
    return settings.STORAGE_SERVICE


# Type alias for injecting storage type directly
StorageTypeDep = Annotated[StorageType, Depends(get_storage_type)]
