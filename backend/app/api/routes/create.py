from fastapi import APIRouter, Depends, HTTPException
from app.schema.user_schema import UserRequest, UserResponse
from app.crud.user_curd import get_user_by_username, create_user
from app.core.securiy import get_password_hash
from app.core.db import get_session
from sqlmodel import Session

route = APIRouter()


@route.post("/create")
def create_new_user(
        request: UserRequest,
        session: Session = Depends(get_session)
):
    # 确认表里没有相同的username
    user = get_user_by_username(request.username, session)
    if user:
        raise HTTPException(status_code=400, detail="存在相同的用户名")

    # 为密码加密
    hashed_password = get_password_hash(request.password)

    # 存入数据库
    new_user = create_user(request.username, hashed_password, session)

    return "用户创建成功"


