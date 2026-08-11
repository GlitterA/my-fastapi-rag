from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.deps import get_vector_store, get_current_user
from langchain_core.vectorstores import VectorStore
from pathlib import Path
from loguru import logger
from app.rag.ingest import ingest_file
from app.model.user_model import User
from app.crud.file_crud import get_file_by_filename, save_file, get_files_by_uploader_name
from app.core.db import get_session
from sqlmodel import Session
import os
route = APIRouter()


DOCUMENTS_DIR = Path(
    os.getenv(
        "DOCUMENTS_DIR",
        "./data/knowledge"
    )
)

DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


@route.post("/upload")
async def upload_document(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        vector_store: VectorStore = Depends(get_vector_store),
        session: Session = Depends(get_session)
):
    # 保存文件
    file_path = DOCUMENTS_DIR / f"{current_user.username}_{file.filename}"

    # if file_path.exists():
    #     raise HTTPException(
    #         status_code=400,
    #         detail="文件已存在"
    #     )
    if get_file_by_filename(file.filename, current_user.username, session):
        raise HTTPException(
            status_code=400,
            detail="文件已存在"
        )
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"上传文件{file.filename}已保存成功")

    # 写入数据库
    save_file(filename=file.filename, uploader_name=current_user.username, session=session)

    logger.info(f"写入文件数据库成功")

    # 写入向量库
    ingest_file(file_path, vector_store, current_user.username, file.filename)

    return {
        "message": "上传成功",
        "filename": file.filename
    }


@route.get("")
def list_documents(
        current_user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
):
    files = get_files_by_uploader_name(
        current_user.username,
        session
    )

    return [
        {
            "filename": file.filename
        }
        for file in files
    ]


@route.delete("/{filename}")
def delete_document(
        filename: str,
        current_user: User = Depends(get_current_user),
        vector_store: VectorStore = Depends(get_vector_store),
        session: Session = Depends(get_session)
):
    result = vector_store.get(
        where={
            "$and": [
                {"source": filename},
                {"uploader": current_user.username}
            ]
        }
    )
    ids = result["ids"]
    if not ids:
        raise HTTPException(
            status_code=404,
            detail="文档不存在"
        )

    # 删向量库
    vector_store.delete(ids)
    file_record = get_file_by_filename(
        filename,
        current_user.username,
        session
    )
    # 删数据库
    if file_record:
        session.delete(file_record)
        session.commit()

    # 删文件
    file = DOCUMENTS_DIR / f"{current_user.username}_{filename}"
    if file.exists():
        file.unlink()

    return {
        "message": "删除成功"
    }
