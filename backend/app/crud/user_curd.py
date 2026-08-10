from app.model.user_model import User
from app.core.security import verify_password
from sqlmodel import Session, select
from app.schema.user_schema import UserResponse

def get_user_by_username(
        username: str,
        session: Session
) -> User:
    stmt = select(User).where(User.username == username)
    return session.exec(statement=stmt).first()


def create_user(
        username: str,
        hashed_password: str,
        session: Session
):
    user = User(
        username=username,
        hashed_password=hashed_password
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def authenticate(username: str, password: str, session: Session) -> User | None:
    db_user = get_user_by_username(username, session)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
