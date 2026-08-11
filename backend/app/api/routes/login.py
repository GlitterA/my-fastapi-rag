from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.model.user_model import Token
from app.crud import user_curd
from datetime import timedelta
from app.core.settings import settings
from app.core.security import create_access_token
from sqlmodel import Session
from app.core.db import get_session
from loguru import logger

route = APIRouter()

@route.post("/login/access-token")
async def login_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: Session = Depends(get_session)
) -> Token:
    """
    为用户生成访问token
    """
    # 验权
    user = user_curd.authenticate(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            user.username, expire_delta=access_token_expires
        )
    )
