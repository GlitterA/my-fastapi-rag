from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.deps import get_vector_store, get_current_user
from langchain_core.vectorstores import VectorStore
from pathlib import Path
from loguru import logger
from app.rag.ingest import ingest_file
from app.model.user_model import User

route = APIRouter()

DOCUMENTS_DIR = Path("./data/knowledge")
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


@route.post("/upload")
async def upload_document(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        vector_store: VectorStore = Depends(get_vector_store)
):
    # 保存文件

    file_path = DOCUMENTS_DIR / file.filename
    if file_path.exists():
        raise HTTPException(
            status_code=400,
            detail="文件已存在"
        )
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"上传文件{file.filename}已保存成功")

    # 写入向量库
    ingest_file(file_path, vector_store, uploader=current_user.username)

    return {
        "message": "上传成功",
        "filename": file.filename
    }


@route.get("")
def list_documents(current_user: User = Depends(get_current_user)):
    documents = []
    for file in DOCUMENTS_DIR.iterdir():
        if file.is_file():
            documents.append(
                {
                    "filename": file.name,
                    "size": file.stat().st_size
                }
            )
    return documents


@route.delete("/{filename}")
def delete_document(
        filename: str,
        current_user: User = Depends(get_current_user),
        vector_store: VectorStore = Depends(get_vector_store)
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

    vector_store.delete(ids)

    file = DOCUMENTS_DIR / filename
    if file.exists():
        file.unlink()

    return {
        "message": "删除成功"
    }
