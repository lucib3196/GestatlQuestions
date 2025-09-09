from api.models.question_model import Topic
from api.data.database import SessionDep
from sqlmodel import select
from typing import Sequence
from sqlalchemy import func
from typing import Union
from typing import Iterable, Sequence, List


def create_topic(session: SessionDep, name: str) -> Topic:
    if not name or not name.lower().strip():
        raise ValueError(f"Topic name cannot be empty")
    name = name.lower().strip()

    result = session.exec(select(Topic).where(func.lower(Topic.name) == name)).first()
    if not result:
        t = Topic(name=name)
        session.add(t)
        session.commit()
        session.refresh(t)
        return t
    else:
        return result


def list_topics(session: SessionDep) -> Sequence[Topic]:
    return session.exec(select(Topic)).all()


def get_topic_by_name(session: SessionDep, name: str) -> Union[Topic, None]:
    stmt = select(Topic).where(func.lower(Topic.name) == name.lower())
    return session.exec(stmt).first()


def get_topics_by_name(session: SessionDep, names: Sequence[str]) -> List[Topic]:
    """
    Return a list of Topic objects that match the given names.
    Ignores None/empty strings in names.
    """
    if not names:
        return []

    topics = []
    for n in names:
        if not n:
            continue
        topic = get_topic_by_name(session, n)
        if topic:
            topics.append(topic)
    return topics


def delete_topic(session: SessionDep, topic: Topic):
    session.delete(topic)
    session.commit()
    session.flush()


def delete_all_topics(session: SessionDep) -> None:
    results = session.exec(select(Topic)).all()
    for t in results:
        delete_topic(session, t)


