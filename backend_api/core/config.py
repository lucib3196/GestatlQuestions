from typing import Optional, Literal

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str
    ENV: Literal["testing", "dev", "production"] = "dev"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl | str] = []
    SECRET_KEY: str
    ALGORITHM: str = "HS256"  # Authentication protocol
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # how long session info is retained
    DATABASE_URI: Optional[str] = None
    AUTH_URL: str = "/auth/login"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SQLITE_DB_PATH: Optional[str] = None

    @field_validator("SQLITE_DB_PATH", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        return v or ":memory:"

    class ConfigDict:
        case_sensitive = True
        env_file = ".env"


settings = Settings(
    PROJECT_NAME="gestalt_question_review",
    BACKEND_CORS_ORIGINS=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    SECRET_KEY="secret_key_need_to_change",
)
