from fastapi import APIRouter, Depends
from typing import Annotated
from pydantic import BaseModel
import backend_api.service.authentication as auth_serv

router = APIRouter(prefix="/auth")


class User(BaseModel):
    display_name: str
    email: str
    password: str


@router.post("/create_user")
async def create_user(user: User):
    return auth_serv.create_user_firebase(user.display_name, user.email, user.password)


@router.get("/userid")
async def get_userid(
    user: Annotated[dict, Depends(auth_serv.get_firebase_user_from_token)],
):
    return {"id": user["uid"]}

