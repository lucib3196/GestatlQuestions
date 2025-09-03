from backend_api.service import user as service
from fastapi import APIRouter, Depends
from backend_api.model.users_model import User
from backend_api.data.database import get_session
from sqlmodel import Session

router = APIRouter(prefix="/user")


@router.post("/create")
async def create_user(user: User, session: Session = Depends(get_session)):
    return await service.create_user(user, session)


@router.get("/get_all/{offset}/{limit}")
async def get_all(
    offset: int = 0, limit: int = 10, session: Session = Depends(get_session)
):
    return await service.get_all_users(session=session, offset=offset, limit=limit)


@router.get("/get_user/{id}")
async def get_user(id: int, session: Session = Depends(get_session)):
    return await service.get_user(session=session, id=id)


@router.post("/delete/{id}")
async def delete_user(id: int, session: Session = Depends(get_session)):
    return await service.delete_user(session, id)
