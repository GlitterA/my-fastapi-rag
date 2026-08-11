from sqlmodel import SQLModel


class FileBody(SQLModel):
    filename: str
    uploader_name: str
