from sqlmodel import SQLModel, Field

# ORM
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False


class User(UserBase, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field(exclude=True)

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
