from app.model.user_model import User
from app.core.securiy import verify_password

saved_username = {"张三": "$2b$12$r36cjRG.pnbVBHb/KBR/muWMMpE51ecyrDi2k81kYW0wBkFZvPSie",
                  "李四": "$2b$12$Z6tJ3OviD.vlDmSnG57TTuV0lZL5mnkNuQxIo6Q78xUqAH7iGokgm",
                  "王五": "$2b$12$Z6tJ3OviD.vlDmSnG57TTuV0lZL5mnkNuQxIo6Q78xUqAH7iGokgm"}


# TODO: 连接数据库后重写方法
def get_user_by_username(username: str) -> User:
    if username in saved_username:
        return User(username=username, hashed_password=saved_username[username])


def authenticate(username: str, password: str) -> User | None:
    db_user = get_user_by_username(username=username)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
