from sqlmodel import SQLModel


class UserRequest(SQLModel):
    username: str
    password: str


class UserResponse(SQLModel):
    username: str
