from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Any
from jose import jwt, JWTError
from app.core.settings import settings
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 从请求头中解析token后交给依赖函数（可以被Depends(oauth2_scheme)取得）
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login/access-token"  # 和登录接口一致
)


def create_access_token(username: str | Any, expire_delta: timedelta) -> str:
    """
    用户登录成功后，生成一个 JWT 字符串
    """
    expire_time = datetime.utcnow() + expire_delta
    to_encode = {"exp": expire_time, "sub": str(username)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY_ACCESS_API, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    将 JWT 字符串解析成字典
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY_ACCESS_API,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
