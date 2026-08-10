from fastapi import APIRouter, UploadFile, File, Depends
from app.core.deps import get_vector_store
from langchain_core.vectorstores import VectorStore
from pathlib import Path
from loguru import logger
from app.rag.ingest import ingest_file

route = APIRouter()

DOCUMENTS_DIR = Path("./data/knowledge")
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

@route.post("/upload")
async def upload_document(
        file: UploadFile = File(...),
        vector_store: VectorStore = Depends(get_vector_store)
):

    # 保存文件

    file_path = DOCUMENTS_DIR / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"上传文件{file.filename}已保存成功")

    # 写入向量库
    ingest_file(file_path, vector_store)

    return {
        "message": "上传成功",
        "filename": file.filename
    }

@route.get("")
def list_documents():
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
        vector_store: VectorStore = Depends(get_vector_store)
):
    result = vector_store.get(
        where={
            "source": filename
        }
    )

    ids = result["ids"]

    vector_store.delete(ids)

    file = DOCUMENTS_DIR / filename
    if file.exists():
        file.unlink()

    return {
        "message":"删除成功"
    }
