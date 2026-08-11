from fastapi import Request
from sqlmodel import Session
from langchain_core.vectorstores import VectorStore
from langchain_core.runnables import Runnable
from app.rag.memory import ChatMemory
from fastapi import Depends, HTTPException, status
from app.core.security import oauth2_scheme, decode_access_token
from app.core.db import get_session
from app.model.user_model import User
from app.crud.user_curd import get_user_by_username


def get_vector_store(request: Request) -> VectorStore:
    return request.app.state.vector_store


def get_rag_chain(request: Request) -> Runnable:
    return request.app.state.rag_chain


def get_chat_memory(request: Request) -> ChatMemory:
    return request.app.state.chat_memory


def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session)
) -> User:
    payload = decode_access_token(token)

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效 token",
        )

    user = get_user_by_username(username, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user
