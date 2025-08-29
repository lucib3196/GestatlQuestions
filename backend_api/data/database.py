import os
from typing import Generator, Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# To do would need to handle the case where I am switching between dev, testing and production databases
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
engine = create_engine(
    f"sqlite:///{DB_PATH}", echo=True, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = SQLModel

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create all tables at startup.
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLModel session."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
