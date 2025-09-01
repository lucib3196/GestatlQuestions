import os
from typing import Generator, Annotated

from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.orm import sessionmaker

from backend_api.core.config import settings


# -------------------------------------------------------------------
# Database Path & URL
# -------------------------------------------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
if settings.ENV == "test":
    # In-memory SQLite for tests
    print("Going into testing mode")
    DATABASE_URL = "sqlite:///:memory:"
else:
    # Local dev database file
    DB_PATH = os.path.join(base_dir, "database.db")
    settings.DATABASE_URI = DB_PATH
    DATABASE_URL = f"sqlite:///{settings.DATABASE_URI}"
# -------------------------------------------------------------------
# Engine & Session Factory
# -------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},  # Only needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = SQLModel


# -------------------------------------------------------------------
# Database Initialization
# -------------------------------------------------------------------
def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


# -------------------------------------------------------------------
# Session Dependency for FastAPI
# -------------------------------------------------------------------
def get_session() -> Generator[Session, None, None]:
    """Yield a SQLModel session per request."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
