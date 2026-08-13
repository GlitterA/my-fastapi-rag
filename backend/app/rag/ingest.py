# 负责文档的加载
from tqdm import tqdm
from loguru import logger
from langchain_core.vectorstores import VectorStore
from app.rag.documents import load_files, load_file
from app.rag.splitter import get_text_splitter
from pathlib import Path
from app.rag.vectorstore import is_empty


def ingest_files(
        source_dir: Path,
        vector_store: VectorStore,
        uploader="system",
        batch_size=20
):
    """
    加载目录下所有支持文件并写入向量数据库

    source_dir:
        原始文档目录

    vector_store:
        向量数据库实例
    """

    if not is_empty(vector_store):
        logger.info("向量库已有数据，跳过全量写入")
        return

    logger.info("向量数据库为空，初始化向量数据库数据...")
    # 加载文档
    documents = load_files(source_dir)

    # 文档切分
    chunks = get_text_splitter().split_documents(documents)

    for i, chunk in enumerate(chunks):
        filename = Path(chunk.metadata["source"]).name
        chunk.metadata["source"] = filename
        chunk.metadata["uploader"] = uploader
        chunk.metadata["chunk_id"] = f"{filename}_{i}"

    for i in tqdm(range(0, len(chunks), batch_size), desc="Ingesting"):
        batch = chunks[i:i + batch_size]
        vector_store.add_documents(batch)


def ingest_file(
        file_path: Path,
        vector_store: VectorStore,
        uploader: str,
        filename: str,
        batch_size=20
):
    # 获取文档
    documents = load_file(file_path)
    logger.info(f"文档名：{documents}")

    # 切分文档
    chunks = get_text_splitter().split_documents(documents)
    # 添加元数据
    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = filename
        chunk.metadata["uploader"] = uploader
        chunk.metadata["chunk_id"] = f"{filename}_{i}"

    # 判重：过滤掉已存在的 chunk_id，保证幂等（重复入库/上传同名文件不会双写）
    existing = vector_store._collection.get(where={"source": filename})
    existing_ids = {
        m.get("chunk_id")
        for m in existing["metadatas"]
        if m
    }
    new_chunks = [
        c for c in chunks
        if c.metadata["chunk_id"] not in existing_ids
    ]

    if not new_chunks:
        logger.info(f"文件 {filename} 的所有 chunk 已在向量库中，跳过")
        return

    logger.info(f"文件 {filename} 新增 {len(new_chunks)} 个 chunk（跳过 {len(chunks) - len(new_chunks)} 个重复）")

    logger.info(f"数据库地址：将文档载入数据库...")
    # 加入数据库
    for i in tqdm(range(0, len(new_chunks), batch_size), desc="Ingesting"):
        batch = new_chunks[i:i + batch_size]
        vector_store.add_documents(batch)
