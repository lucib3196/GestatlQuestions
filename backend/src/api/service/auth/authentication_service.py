from datetime import datetime, timedelta, timezone
import bcrypt

from jose import jwt
from src.api.core.config import settings


# Hashes password
def encrypt_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# Verifys password
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# Creates JWT plus experation data
def generate_token(username: str, expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
    data = {"sub": username}
    expires = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    data |= {"exp": expires}
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# dECODE
def decode_token(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
