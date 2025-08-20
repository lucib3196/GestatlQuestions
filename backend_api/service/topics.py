# Standard library

# Third-party
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

# Local
from backend_api.data.database import SessionDep
from backend_api.model.questions_models import Topic

from typing import Tuple

async def get_or_create_topic(session: SessionDep, name: str) -> Tuple[Topic, bool]:
    name = name.strip()
    if not name:
        raise ValueError("Topic cannot be empty")

    exising = session.exec(select(Topic).where(Topic.name == name)).first()
    if exising:
        return exising, True

    topic = Topic(name=name)
    session.add(topic)
    try:
        session.commit()
        session.refresh(topic)
        return topic, True
    except IntegrityError:
        session.rollback()
        existing = session.exec(
            select(Topic).where(Topic.name == name).limit(1)
        ).first()
        if existing:
            return existing, False
        raise
