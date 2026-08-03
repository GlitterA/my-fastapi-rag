from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Any
from jose import jwt
from core.config import settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: str | Any, expire_delta: timedelta) -> str:
    expire_time = datetime.utcnow() + expire_delta
    to_encode = {"exp": expire_time, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY_ACCESS_API, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)




