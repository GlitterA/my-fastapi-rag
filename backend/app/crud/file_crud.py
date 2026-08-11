from sqlmodel import Session, select
from app.model.file_model import File
from typing import Sequence


def get_file_by_filename(
        filename: str,
        uploader_name: str,
        session: Session
) -> File:
    stmt = select(File).where(
        File.filename == filename,
        File.uploader_name == uploader_name
    )
    return session.exec(statement=stmt).first()


def get_files_by_uploader_name(
        uploader_name: str,
        session: Session

) -> Sequence[File]:
    stmt = select(File).where(
        File.uploader_name == uploader_name
    )
    return session.exec(statement=stmt).all()


def save_file(
        filename: str,
        uploader_name: str,
        session: Session
):
    file = File(
        filename=filename,
        uploader_name=uploader_name
    )

    session.add(file)
    session.commit()
    session.refresh(file)

    return file
