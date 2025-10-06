# --- Standard Library ---
import os
from pathlib import Path
from typing import Optional, Literal

# --- Third-Party ---
from dotenv import load_dotenv
from pydantic import AnyHttpUrl, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings

load_dotenv()


class AppSettings(BaseSettings):
    PROJECT_NAME: str
    ENV: Literal["testing", "dev", "production"] = "dev"
    STORAGE_SERVICE: Literal["local", "cloud"] = "local"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl | str] = []
    SECRET_KEY: str

    # User authentication
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_URL: str = "/auth/login"

    # Database Settings
    DATABASE_URI: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    # Cloud Storage
    FIREBASE_PATH: Optional[str | Path] = None
    STORAGE_BUCKET: Optional[str] = None

    # Static Directory
    QUESTIONS_DIRNAME: str | Path
    QUESTIONS_PATH: str | Path
    BASE_PATH: str | Path

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

# TODO Change this to an environment variable
BASE_DIR = Path(__file__).resolve().parents[4]

settings = AppSettings(
    PROJECT_NAME="gestalt_question_review",
    BACKEND_CORS_ORIGINS=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    SECRET_KEY=os.getenv("SECRET_KEY", ""),
    FIREBASE_PATH=Path(BASE_DIR) / str(os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")),
    STORAGE_BUCKET=os.getenv("STORAGE_BUCKET"),
    QUESTIONS_DIRNAME="questions",  # relative folder name only
    QUESTIONS_PATH=BASE_DIR / "questions",  # absolute path resolved against BASE_DIR
    BASE_PATH=BASE_DIR,
)
