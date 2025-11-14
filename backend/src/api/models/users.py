from src.api.models.models import UserRole
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str | None
    email: str | None
    role: UserRole = UserRole.STUDENT
    fb_id: str | None = None
    storage_path: str | None = None
