from typing import Annotated, Literal
from fastapi import Depends
from src.api.core.config import get_settings


app_settings = get_settings()

storage_type = Literal["local", "cloud"]


async def get_storage_service_type() -> storage_type:
    return app_settings.STORAGE_SERVICE


StorageType = Annotated[storage_type, Depends(get_storage_service_type)]
