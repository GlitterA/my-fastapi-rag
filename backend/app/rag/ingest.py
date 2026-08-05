# 负责文档的加载

from langchain_core.vectorstores import VectorStore
from app.rag.documents import load_documents
from app.rag.splitter import get_text_splitter
from loguru import logger


def ingest_documents(
        source_dir: str,
        vector_store: VectorStore,
        batch_size=20
):
    """
    加载文件并写入向量数据库

    source_dir:
        原始文档目录

    vector_store:
        向量数据库实例
    """

    # 检查是否已有数据，避免重复写入
    existing = vector_store.get(limit=1, include=[])
    if existing["ids"]:
        logger.info("向量库中已存在数据，跳过文档写入")
        return
    # 加载文档
    documents = load_documents(source_dir)
    logger.info(f"已加载 {len(documents)} 个文档")

    # 文档切分
    chunks = get_text_splitter().split_documents(documents)
    logger.info(f"切分后共 {len(chunks)} 个文本块")

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        vector_store.add_documents(batch)