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

    # 加载文档
    documents = load_files(source_dir)

    # 文档切分
    chunks = get_text_splitter().split_documents(documents)

    for chunk in chunks:
        chunk.metadata["uploader"] = uploader

    for i in tqdm(range(0, len(chunks), batch_size), desc="Ingesting"):
        batch = chunks[i:i + batch_size]
        vector_store.add_documents(batch)


def ingest_file(
        file_path: Path,
        vector_store: VectorStore,
        uploader: str,
        batch_size=20
):
    # 获取文档
    documents = load_file(file_path)
    logger.info(f"文档名：{documents}")

    # 切分文档
    chunks = get_text_splitter().split_documents(documents)
    # 添加元数据
    for chunk in chunks:
        chunk.metadata["source"] = file_path.name
        chunk.metadata["uploader"] = uploader

    logger.info(f"切分后的文档：{chunks}")

    logger.info("将文档载入数据库...")
    # 加入数据库
    for i in tqdm(range(0, len(chunks), batch_size), desc="Ingesting"):
        batch = chunks[i:i + batch_size]
        vector_store.add_documents(batch)
