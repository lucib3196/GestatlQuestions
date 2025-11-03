from src.api.database import SessionDep
from src.api.models.models import Language, QType, Topic
from src.api.database.generic_db import create_or_resolve


def create_qtype(name: str, session: SessionDep) -> QType:
    return create_or_resolve(QType, name, session)[0]


def create_qtopic(name: str, session: SessionDep) -> Topic:
    return create_or_resolve(Topic, name, session)[0]


def create_language(name: str, session: SessionDep) -> Language:
    return create_or_resolve(Language, name, session)[0]
