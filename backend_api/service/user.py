from backend_api.data.database import SessionDep
from backend_api.model.users import User
from typing import Annotated
from fastapi import Query
from sqlmodel import select

from collections.abc import Sequence


async def create_user(user: User, session: SessionDep) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


async def get_users(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
) -> Sequence[User]:
    result = session.exec(select(User).offset(offset).limit(limit))
    users = result.all()
    return users


async def get_user(session: SessionDep, id: int):
    result = session.exec(select(User).where(User.id == id)).first()
    if not result:
        return {"detail": "User Not Found"}
    else:
        return result


async def delete_user(session: SessionDep, id: int):
    user = await get_user(session, id=id)
    if not isinstance(user, User):
        return {"detail", "Cannot Delete User. Does not exit"}
    session.delete(user)
    session.commit()
    return {"ok": True}
