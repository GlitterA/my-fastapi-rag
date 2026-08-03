from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False


class User(UserBase):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
