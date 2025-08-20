# Standard library

# Third-party
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

# Local
from backend_api.data.database import SessionDep

from typing import Tuple
from backend_api.model.questions_models import Language


async def get_or_create_language(session: SessionDep, name: str) -> Tuple[Language, bool]:
    name = name.strip()
    if not name:
        raise ValueError("Language cannot be empty")

    exising = session.exec(select(Language).where(Language.name == name)).first()
    if exising:
        return exising, True

    lang = Language(name=name)
    session.add(lang)
    try:
        session.commit()
        session.refresh(lang)
        return lang, True
    except IntegrityError:
        session.rollback()
        existing = session.exec(
            select(Language).where(Language.name == name).limit(1)
        ).first()
        if existing:
            return existing, False
        raise
