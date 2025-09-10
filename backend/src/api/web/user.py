from src.api.service import user as service
from fastapi import APIRouter, Depends
from src.api.models.users_model import User
from src.api.database import SessionDep
from sqlmodel import Session

router = APIRouter(prefix="/user")


@router.post("/create")
async def create_user(user: User, session: SessionDep):
    return await service.create_user(user, session)


@router.get("/get_all/{offset}/{limit}")
async def get_all(
    session: SessionDep,
    offset: int = 0,
    limit: int = 10,
):
    return await service.get_all_users(session=session, offset=offset, limit=limit)


@router.get("/get_user/{id}")
async def get_user(id: int, session: SessionDep):
    return await service.get_user(session=session, id=id)


@router.post("/delete/{id}")
async def delete_user(id: int, session: SessionDep):
    return await service.delete_user(session, id)
