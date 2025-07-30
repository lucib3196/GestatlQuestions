from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin.auth import verify_id_token, create_user, UserRecord

bearer_scheme = HTTPBearer(auto_error=False)


def create_user_firebase(display_name: str, email: str, password: str):
    try:
        user: UserRecord = create_user(
            display_name=display_name, email=email, password=password
        )
        return {"userId": user.uid, "username": user.email}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"User already exist\n {e}"
        )


def get_firebase_user_from_token(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict | None:
    print(token)
    try:
        if not token:
            raise ValueError("No token")

        user = verify_id_token(token.credentials)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in or invalide credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
