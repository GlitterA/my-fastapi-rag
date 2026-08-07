from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.model.user_model import Token
from app.crud import user_curd
from datetime import timedelta
from app.core.settings import settings
from app.core.securiy import create_access_token

route = APIRouter()

@route.post("/login/access-token")
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) \
        -> Token:
    """
    为用户生成访问token
    """
    # 验权
    user = user_curd.get_user_by_username(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            user.username, expire_delta=access_token_expires
        )
    )
