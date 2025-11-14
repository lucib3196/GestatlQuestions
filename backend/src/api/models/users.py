from src.api.models.models import UserRole
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str
    role: UserRole = UserRole.STUDENT
    fb_id: str
    storage_path: str | None = None
