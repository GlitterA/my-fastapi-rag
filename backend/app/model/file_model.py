from sqlmodel import SQLModel, Field


class File(SQLModel, table=True):
    __tablename__ = "file"

    id: int = Field(default=None, primary_key=True)
    filename: str
    uploader_name: str
