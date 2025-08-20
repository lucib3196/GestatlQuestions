# Standard library

# Third-party
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

# Local
from backend_api.data.database import SessionDep

from typing import Tuple
from backend_api.model.questions_models import QType


async def get_or_create_Qtype(session: SessionDep, name: str) -> Tuple[QType, bool]:
    name = name.strip()
    if not name:
        raise ValueError("Language cannot be empty")

    exising = session.exec(select(QType).where(QType.name == name)).first()
    if exising:
        return exising, True

    qtype = QType(name=name)
    session.add(qtype)
    try:
        session.commit()
        session.refresh(qtype)
        return qtype, True
    except IntegrityError:
        session.rollback()
        existing = session.exec(
            select(QType).where(QType.name == name).limit(1)
        ).first()
        if existing:
            return existing, False
        raise
