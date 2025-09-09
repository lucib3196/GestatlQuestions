import os
from pathlib import Path
from typing import Annotated, Generator

from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from src.api.core import settings, logger

load_dotenv()

# Define choosing the settings
if settings.ENV == "testing":
    DATABASE_URL = "sqlite:///:memory:"
elif settings.ENV == "production":
    DATABASE_URL = os.getenv("POSTGRES_URL")
    if not DATABASE_URL:
        raise RuntimeError("POSTGRES_URL must be set in production mode")
elif settings.ENV == "dev":
    # Local Development database is stored within the same directory as this file
    base_dir = Path(__file__).parent.resolve()
    database_path = Path(base_dir / "database.db").resolve()
    DATABASE_URL = f"sqlite:///{database_path}"
    # raise NotImplementedError("Development database is not ready yet")
else:
    raise ValueError(f"Unknown environment: {settings.ENV}")

# Redundant but just incase
settings.DATABASE_URL = DATABASE_URL
logger.info(
    f"Database Settings set to {settings.ENV} Database URL: {settings.DATABASE_URL}"
)

# Connection Arguments
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}  # Only needed for SQLite
engine = create_engine(url=settings.DATABASE_URL, echo=True, connect_args=connect_args)

Base = SQLModel


# -------------------------------------------------------------------
# Database Initialization
# -------------------------------------------------------------------
def create_db_and_tables(engine=engine):
    Base.metadata.create_all(engine)
    return engine


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLModel session per request."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
